import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
 
def create_features(df, is_future=False):
    """
    创建时间序列特征
    :param df: 输入DataFrame
    :param is_future: 是否为未来预测数据
    :return: 包含特征的DataFrame
    """
    df = df.copy()

    # 基础时间特征
    df['dayofweek'] = df.index.dayofweek
    df['weekend'] = (df.index.dayofweek >= 5).astype(int)
    df['month'] = df.index.month

    # 特殊日期标记
    df['double11'] = ((df.index.month == 11) & (df.index.day == 11)).astype(int)
    df['double12'] = ((df.index.month == 12) & (df.index.day == 12)).astype(int)
    df['newyear'] = ((df.index.month == 1) & (df.index.day == 1)).astype(int)

    # 如果不是未来数据，添加统计特征
    if not is_future:
        if 'comments' in df.columns:
            # 滚动统计特征
            df['7day_avg'] = df['comments'].rolling(7).mean()
            df['7day_std'] = df['comments'].rolling(7).std()

            # 滞后特征
            for i in range(1, 8):
                df[f'lag_{i}'] = df['comments'].shift(i)

    return df

def predict_sales(start_date, end_date, future_start_date, future_end_date):
    # 数据准备
    df = pd.read_excel('data/评论_真维斯_清洗后.xlsx')
    df['rateDate'] = pd.to_datetime(df['rateDate'])
    peak_df = df[(df['rateDate'] >= start_date) & (df['rateDate'] <= end_date)]
    daily_comments = peak_df.resample('D', on='rateDate').size()
    daily_comments = daily_comments.reindex(pd.date_range(start=start_date, end=end_date), fill_value=0)

    df_rf = pd.DataFrame({'comments': daily_comments})
    df_rf = create_features(df_rf).dropna()

    X = df_rf.drop('comments', axis=1)
    y = df_rf['comments']

    # 优化随机森林模型
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X, y)

    # 预测未来
    future_dates = pd.date_range(start=future_start_date, end=future_end_date)
    future_df = pd.DataFrame(index=future_dates)
    future_df = create_features(future_df, is_future=True)

    # 初始化滞后特征
    last_window = df_rf['comments'].values[-7:]

    predictions = []
    for date in future_dates:
        temp_df = pd.DataFrame(index=[date])
        temp_df = create_features(temp_df, is_future=True)

        # 添加滞后特征
        for i in range(1, 8):
            if i <= len(last_window):
                temp_df[f'lag_{i}'] = last_window[-i]
            else:
                temp_df[f'lag_{i}'] = 0

        # 添加滚动统计特征
        if len(predictions) >= 7:
            temp_df['7day_avg'] = np.mean(predictions[-7:])
            temp_df['7day_std'] = np.std(predictions[-7:])
        else:
            # 使用历史数据的统计特征
            temp_df['7day_avg'] = df_rf['7day_avg'].iloc[-1]
            temp_df['7day_std'] = df_rf['7day_std'].iloc[-1]

        # 确保所有需要的特征都存在
        for col in X.columns:
            if col not in temp_df:
                temp_df[col] = 0

        # 预测当日值
        current_features = temp_df[X.columns].fillna(0)
        pred = max(0, model.predict(current_features)[0])
        predictions.append(pred)

        # 更新最后窗口
        last_window = np.append(last_window[1:], pred)

    pred_index = pd.date_range(start=future_start_date, periods=len(predictions))
    return daily_comments, pred_index, predictions

# 预测分析函数
def predict_and_analyze():
    start_date = '2015-11-01'
    end_date = '2016-01-31'
    future_start_date = '2016-02-01'
    future_end_date = '2016-03-01'
    
    # 生成未来日期序列
    future_dates = pd.date_range(start=future_start_date, end=future_end_date)

    daily_comments, pred_index, predictions = predict_sales(start_date, end_date, future_start_date, future_end_date)

    result_df = pd.DataFrame({
    '日期': future_dates,
    '预测销量': predictions,
    '7天平滑值': pd.Series(predictions).rolling(7, min_periods=1).mean()
    })

    return daily_comments, pred_index, predictions, result_df
