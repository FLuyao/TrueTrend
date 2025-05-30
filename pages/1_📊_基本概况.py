import streamlit as st
import altair as alt
from analysis.真维斯数据展示 import load_and_process_data
from analysis.真维斯颜色方面统计 import load_color_data
from analysis.真维斯销售与时间统计 import sales_time_analysis
from analysis.真维斯其他方面统计 import get_sentiment_distribution

st.set_page_config(page_title="基本概况", page_icon="📊")

st.markdown("# 基本概况")
st.sidebar.header("基本概况")
st.write(
    """本页面展示了真维斯品牌的销售概况、
    颜色销售统计、销售与时间的关系以及评论情感分布等信息。
    通过这些图表，你可以直观地了解品牌的销售趋势和消费者偏好。"""
)

# ===================== 基本销售统计可视化模块 ====================
# 加载数据
all_by_quantity, all_by_revenue = load_and_process_data()

# 显示销售量图表
st.markdown("### 商品销售量统计")
all_by_quantity = all_by_quantity.reset_index()
all_by_quantity.columns = ['商品编号', '销售量']
st.altair_chart(
    alt.Chart(all_by_quantity).mark_bar().encode(
        x=alt.X('商品编号:N', sort='-y'),
        y=alt.Y('销售量:Q', title='销售量'),
        color=alt.value('#4B96E9')  
    ).interactive()
)

# 显示销售额图表 
st.markdown("### 商品销售额统计")
all_by_revenue = all_by_revenue.reset_index()
all_by_revenue.columns = ['商品编号', '销售额']
st.altair_chart(
    alt.Chart(all_by_revenue).mark_bar().encode(
        x=alt.X('商品编号:N', sort='-y'),
        y=alt.Y('销售额:Q', title='销售额'),
        color=alt.value('#FF6B6B')  
    ).interactive()
)

# 显示统计信息
with st.sidebar:
    st.markdown("### 统计摘要")
    st.metric("平均销量", f"{all_by_quantity['销售量'].mean():,.0f}件")
    st.metric("平均销售额", f"¥{all_by_revenue['销售额'].mean():,.0f}")

# ===================== 颜色统计可视化模块 ====================
# 加载数据
quantity_top10_colors, revenue_top10_colors = load_color_data()

# 显示销售量最高的10种颜色商品
st.markdown("### 销售量最高的10种颜色商品")
color_data_qty = quantity_top10_colors.reset_index()
color_data_qty.columns = ['颜色', '销售量']

# 自定义颜色映射
color_mapping = {
    '黑色': '#000000',
    '深蓝色': '#00008B',
    '宝蓝色': '#1E90FF',
    '中蓝色': '#4169E1',
    '浅蓝色': '#87CEFA',
    '中灰色': "#9C9C9C",
    '青军绿': '#556B2F',
    '靛蓝色': "#4B0082",
    '深花灰': "#484747",
    '彩蓝': '#4682B4'
}

st.altair_chart(
    alt.Chart(color_data_qty).mark_bar().encode(
        x=alt.X('颜色:N', sort='-y', axis=alt.Axis(labelAngle=0)),  
        y=alt.Y('销售量:Q', title='总销售量'),
        color=alt.Color('颜色:N', scale=alt.Scale(domain=list(color_mapping.keys()),
                                                range=list(color_mapping.values())),
                        legend=None), 
    ).interactive()
)

# 颜色销售额Top10
st.markdown("### 销售额最高的10种颜色商品")
color_data_rev = revenue_top10_colors[['商品颜色', '总销售额']].copy()
color_data_rev.columns = ['颜色', '销售额']


# 自定义颜色映射
color_mapping = {
    '黑色': '#000000',
    '深蓝色': '#00008B',
    '宝蓝色': '#1E90FF',
    '中蓝色': '#4169E1',
    '浅蓝色': '#87CEFA',
    '米白': '#F5F5DC',
    '青军绿': '#556B2F',
    '水蓝色': '#ADD8E6',
    '橙红': '#FF4500',
    '彩蓝': '#4682B4'
}

# 构造Altair图表
st.altair_chart(
    alt.Chart(color_data_rev).mark_bar().encode(
        x=alt.X('颜色:N', sort='-y', axis=alt.Axis(labelAngle=0)),  
        y=alt.Y('销售额:Q', title='总销售额'),
        color=alt.Color('颜色:N', scale=alt.Scale(domain=list(color_mapping.keys()),
                                                range=list(color_mapping.values())),
                        legend=None), 
    ).interactive()
)

# ===================== 销售与时间的统计可视化模块 ====================
# 加载数据
daily_counts, monthly_counts, peak_daily = sales_time_analysis()

# 显示每日销售数量统计
st.markdown("### 每日销售数量统计")
daily_counts = daily_counts.reset_index()
daily_counts.columns = ['日期', '销售量']
st.altair_chart(
    alt.Chart(daily_counts).mark_area().encode(
        x=alt.X('日期:T', title='日期', sort='ascending'),
        y=alt.Y('销售量:Q', title='销售量'),
        color=alt.value('#4B96E9')
    ).interactive()
)

# 显示每月销售数量统计
st.markdown("### 月度销售数量统计")
monthly_counts = monthly_counts.to_timestamp()
monthly_counts = monthly_counts.reset_index()
monthly_counts.columns = ['月份', '销售量']
st.altair_chart(
    alt.Chart(monthly_counts).mark_line().encode(
        x=alt.X('月份:T', title='月份', sort='ascending'),
        y=alt.Y('销售量:Q', title='销售量'),
        color=alt.value('#FF6B6B')
    ).interactive()
)

# 显示高峰期间每日销售趋势
st.markdown("### 高峰期间每日销售趋势")
peak_daily = peak_daily.reset_index()
peak_daily.columns = ['日期', '销售量']
st.altair_chart(
    alt.Chart(peak_daily).mark_line().encode(
        x=alt.X('日期:T', title='日期', sort='ascending'),
        y=alt.Y('销售量:Q', title='销售量'),
        color=alt.value("#3EAB5F")
    ).interactive()
)

# ===================== 评论情感统计可视化模块 ====================
# 加载数据
sentiment_stats = get_sentiment_distribution()

# 显示情感分布图表
st.markdown("### 评论情感分布")
sentiment_stats = sentiment_stats.reset_index()
sentiment_stats.columns = ['情感分类', '数量']
st.altair_chart(
    alt.Chart(sentiment_stats).mark_arc().encode(
        theta=alt.Theta('数量:Q', title='评论数量'),
        color=alt.Color('情感分类:N', title='情感分类')
    ).interactive()
)

st.button("重新加载")