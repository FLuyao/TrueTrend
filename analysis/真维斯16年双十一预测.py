import pandas as pd
import numpy as np

def predict_sales_11():
    """
    预测2016年11月每日销售数量
    """
    # 读取Excel文件
    df = pd.read_excel('data/评论_真维斯_清洗后.xlsx')
    
    # 检查rateDate是否已经是datetime格式
    if not pd.api.types.is_datetime64_any_dtype(df['rateDate']):
        df['rateDate'] = pd.to_datetime(df['rateDate'])
    
    # 提取2014年11月和2015年11月的销售数据
    nov_2014 = df[(df['rateDate'].dt.year == 2014) & (df['rateDate'].dt.month == 11)]
    nov_2015 = df[(df['rateDate'].dt.year == 2015) & (df['rateDate'].dt.month == 11)]
    
    # 计算每月的销售总数
    count_2014 = len(nov_2014)
    count_2015 = len(nov_2015)
    
    print(f"2014年11月销售数量: {count_2014}")
    print(f"2015年11月销售数量: {count_2015}")
    
    if count_2014 == 0 or count_2015 == 0:
        raise ValueError("2014年或2015年11月没有销售数据")
    
    # 计算年增长率
    growth_rate = (count_2015 - count_2014) / count_2014
    
    # 应用相同的增长率预测2016年
    pred_2016 = int(count_2015 * (1 + growth_rate))
    
    # 限制最大增长不超过50%，防止异常值
    max_growth = int(count_2015 * 1.5)
    pred_2016 = min(pred_2016, max_growth)
    
    print(f"预测2016年11月总销售数量: {pred_2016}")
    
    # 计算2015年11月每天的销售数量（主要参考2015年数据）
    daily_2015 = nov_2015.groupby(nov_2015['rateDate'].dt.day).size()
    
    # 计算2015年每日占比
    if count_2015 > 0:
        daily_ratio = daily_2015 / count_2015
    else:
        daily_ratio = pd.Series(np.ones(30)/30, index=range(1, 31))
    
    # 预测2016年11月每天的销售数量
    daily_2016 = (daily_ratio * pred_2016).round().astype(int)
    
    # 确保总和等于预测总量
    while daily_2016.sum() != pred_2016:
        diff = int(pred_2016 - daily_2016.sum())
        if diff > 0:
            daily_2016[np.argmin(daily_2016)] += 1
        else:
            daily_2016[np.argmax(daily_2016)] -= 1
    
    # 创建完整日期范围
    days = range(1, 31)
    daily_pred = pd.Series(daily_2016, index=days).reindex(days, fill_value=0)
    
    # 结果整理
    result = pd.DataFrame({
        '日期': [f"2016-11-{day:02d}" for day in days],
        '预测销量': daily_pred.values
    })
    
    return days, daily_pred, result
