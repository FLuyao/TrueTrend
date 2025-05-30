import pandas as pd
import re
import streamlit as st

@st.cache_data
def load_color_data():
    """加载并处理颜色相关数据"""
    # 读取数据
    df_sales = pd.read_excel("data/真维斯_商品销售统计.xlsx")
    df_reviews = pd.read_excel("data/评论_真维斯_清洗后.xlsx")
    
    def extract_unified_color(sku):
        """
        统一颜色提取函数，处理以下中文格式：
        1. "颜色:芥黄 2460;尺码:M" → 提取"芥黄"
        2. "颜色:2660 湖蓝色;尺码:L" → 提取"湖蓝色" 
        3. "颜色分类:黑色;尺码:M" → 提取"黑色"
        """
        if pd.isna(sku):
            return '未知颜色'
            
        sku = str(sku).strip()
        
        # 中文颜色前缀列表（按优先级排序）
        color_prefixes = ['颜色:', '颜色分类:']
        
        # 提取颜色字段部分
        color_part = None
        for prefix in color_prefixes:
            if prefix in sku:
                color_part = sku.split(prefix)[1].split(';')[0].strip()
                break
                
        if not color_part:
            return '未知颜色'
        
        # 清洗数字和多余空格
        color = re.sub(r'\d+', '', color_part).strip()  # 移除所有数字
        color = re.sub(r'\s+', ' ', color).strip()      # 合并多余空格
        
        return color if color else '未知颜色'

    
    # 处理数据
    df_reviews["颜色"] = df_reviews["auctionSku"].apply(extract_unified_color)
    
    # 销量Top10颜色
    df_merged = pd.merge(
        df_sales,
        df_reviews[["_itemnumber_", "颜色"]],
        on="_itemnumber_",
        how="inner"
    )
    color_stats = df_merged[df_reviews["颜色"] != '未知颜色'] \
        .groupby("颜色")["comment_count"].sum().nlargest(10)
    
    # 颜色销售额分析
    df_sales_clean = df_sales.drop_duplicates('_itemnumber_', keep='last')
    df_reviews_clean = df_reviews.drop_duplicates('_itemnumber_', keep='last')
    merged_df = pd.merge(df_sales_clean, df_reviews_clean, on='_itemnumber_', how='left')
    merged_df['商品颜色'] = merged_df['auctionSku'].apply(extract_unified_color)
    
    color_sales = merged_df.groupby('商品颜色').agg({
        'comment_count': 'sum',
        'estimated_price_by_sales': 'mean',
        '_itemnumber_': 'nunique'
    }).reset_index()
    
    color_sales.columns = ['商品颜色', '总销量', '平均价格', '商品数量']
    color_sales['总销售额'] = color_sales['总销量'] * color_sales['平均价格']
    
    valid_colors = color_sales[color_sales['商品颜色'] != '未知颜色'].sort_values('总销售额', ascending=False).head(10)
    if valid_colors.empty:
        print("警告：没有找到有效颜色数据，使用所有颜色数据")
        valid_colors = color_sales.sort_values('总销售额', ascending=False).head(10)
    
    return color_stats, valid_colors
