import pandas as pd
import streamlit as st

@st.cache_data  
def load_and_process_data():
    """加载并处理数据，返回销售量和销售额数据"""
    # 读取数据
    df_sales = pd.read_excel("data/真维斯_商品销售统计.xlsx")
    df_reviews = pd.read_excel("data/评论_真维斯_清洗后.xlsx")
    
    # 计算销售总额
    df_sales['total_sales'] = df_sales['estimated_price_by_sales'] * df_sales['comment_count']
    
    # 合并数据并按商品编号排序
    df_merged = pd.merge(
        df_sales[["_itemnumber_", "comment_count", "total_sales"]],
        df_reviews[["_itemnumber_"]].drop_duplicates(),
        on="_itemnumber_",
        how="inner"
    ).sort_values('_itemnumber_')
    
    # 计算分组数据
    all_by_quantity = df_merged.groupby("_itemnumber_")["comment_count"].sum()
    all_by_revenue = df_merged.groupby("_itemnumber_")["total_sales"].sum()
    
    return all_by_quantity, all_by_revenue


