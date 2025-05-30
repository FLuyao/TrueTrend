import streamlit as st

st.set_page_config(
    page_title="TrueTrend",
    page_icon="👋",
)

st.write("# 欢迎来到 TrueTrend! 👋")

st.sidebar.success("选择上方的菜单栏，以查看真维斯评论数据分析结果。")

st.markdown(
    """
    ### 👈左侧菜单栏分别为：
    - 首页：当前页面
    - 基本概况：显示销售基本分析概况
    - 预测分析：显示销售预测分析结果
    - 对比分析：显示与竞争对手优衣库的销售情况对比分析结果
"""
)