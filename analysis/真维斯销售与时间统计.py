import pandas as pd
import streamlit as st
@st.cache_data
def sales_time_analysis():
    df = pd.read_excel("data/评论_真维斯_清洗后.xlsx")
    df['rateDate'] = pd.to_datetime(df['rateDate'])  # 确保日期格式正确

    # 基础统计
    daily_counts = df['rateDate'].dt.date.value_counts().sort_index()
    monthly_counts = df['rateDate'].dt.to_period('M').value_counts().sort_index()
    
    # 高峰期间分析 (2015-11 至 2016-01)
    peak_df = df[(df['rateDate'] >= '2015-11-01') & 
                (df['rateDate'] <= '2016-01-31')]
    peak_daily = peak_df.resample('D', on='rateDate').size()
    peak_daily = peak_daily.reindex(
        pd.date_range(start='2015-11-01', end='2016-01-31'),
        fill_value=0
    )
    
    return daily_counts, monthly_counts, peak_daily


