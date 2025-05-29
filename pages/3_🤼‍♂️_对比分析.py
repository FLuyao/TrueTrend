import streamlit as st
import pandas as pd
import altair as alt
from analysis.真维斯优衣库对比分析 import BrandSalesAnalyzer

@st.cache_data
def load_data():
    analyzer = BrandSalesAnalyzer("data\评论_真维斯_清洗后.xlsx", "data\\reviews_uni_clean.xlsx", "data\真维斯_商品销售统计.xlsx")
    analyzer.preprocess()
    analyzer.compare_total_sales()
    monthly_trends_data = analyzer.get_monthly_trends_data()
    top_items_data = analyzer.get_top_items_data()
    satisfaction_distribution_data = analyzer.get_satisfaction_distribution_data()
    sku_distributions_data = analyzer.get_sku_distributions_data()
    return monthly_trends_data, top_items_data, satisfaction_distribution_data, sku_distributions_data

st.set_page_config(page_title="对比分析", page_icon="🤼‍♂️")

st.markdown("# 对比分析")
st.sidebar.header("对比分析")
st.write(
    """本页面展示了真维斯和优衣库品牌的销售量对比、
    热销商品对比、满意度等级分布对比以及热门颜色和尺码对比等信息。
    通过这些对比图表，你可以直观地了解两个品牌在不同方面的表现差异。"""
)

# 加载数据
months, jw_counts, uq_counts = load_data()[0]
jw_top_items, jw_top_counts, uq_top_items, uq_top_counts = load_data()[1]
levels, jw_levels, uq_levels = load_data()[2]
colors_j_top, colors_u_top, sizes_j_top, sizes_u_top = load_data()[3]

# 计算一些统计信息
total_comments_jw = sum(jw_counts)
total_comments_uq = sum(uq_counts)


# 在侧边栏添加统计信息
st.sidebar.markdown("### 统计信息")
st.sidebar.metric(label="真维斯 总评论数量", value=total_comments_jw)
st.sidebar.metric(label="优衣库 总评论数量", value=total_comments_uq)


# ===================== 月度评论量趋势对比可视化模块 ====================
monthly_trends_df = pd.DataFrame({"月份": months, "真维斯": jw_counts, "优衣库": uq_counts})
monthly_trends_chart = alt.Chart(monthly_trends_df).transform_fold(
    ["真维斯", "优衣库"],
    as_=["品牌", "评论数量"]
).mark_line().encode(
    x=alt.X("月份:T", title="时间"),
    y=alt.Y("评论数量:Q", title="评论数量"),
    color=alt.Color("品牌:N", title="品牌", scale=alt.Scale(domain=["真维斯", "优衣库"], range=["blue", "orange"]))
)
st.markdown("### 月度评论量趋势对比（近似销售量）")
st.altair_chart(monthly_trends_chart.interactive())

# ===================== 热销商品Top10对比可视化模块 ====================
# 真维斯热销商品 Top10 图表
top_items_jw_df = pd.DataFrame({"商品编号": jw_top_items.values, "评论数量": jw_top_counts.values})
top_items_jw_df["品牌"] = "真维斯"  # 添加品牌字段
top_items_jw_chart = alt.Chart(top_items_jw_df).mark_bar().encode(  
    x=alt.X("商品编号:N", title="商品编号", sort="-y"),
    y=alt.Y("评论数量:Q", title="评论数量"),
    color=alt.Color("品牌:N", title="品牌", scale=alt.Scale(domain=["真维斯", "优衣库"], range=["blue", "orange"]))
).properties(
    title="真维斯 - 热销商品 Top10",
    width=275  
)

# 优衣库热销商品 Top10 图表
top_items_uq_df = pd.DataFrame({"商品编号": uq_top_items.values, "评论数量": uq_top_counts.values})
top_items_uq_df["品牌"] = "优衣库"  # 添加品牌字段
top_items_uq_chart = alt.Chart(top_items_uq_df).mark_bar().encode(
    x=alt.X("商品编号:N", title="商品编号", sort="-y"),
    y=alt.Y("评论数量:Q", title="评论数量"),
    color=alt.Color("品牌:N", title="品牌", scale=alt.Scale(domain=["真维斯", "优衣库"], range=["blue", "orange"]))
).properties(
    title="优衣库 - 热销商品 Top10",
    width=275  
)

# 将热销商品 Top10 图表并排显示
top_items_chart = alt.hconcat(top_items_jw_chart, top_items_uq_chart).resolve_scale(x='independent')
st.markdown("### 热销商品 Top10 对比")
st.altair_chart(top_items_chart.interactive())

# ===================== 满意度等级分布对比可视化模块 ====================
satisfaction_distribution_df = pd.DataFrame({"满意度等级": levels, "真维斯": jw_levels, "优衣库": uq_levels})
satisfaction_distribution_chart = alt.Chart(satisfaction_distribution_df).transform_fold(
    ["真维斯", "优衣库"],
    as_=["品牌", "评论数量"]
).mark_bar().encode(
    x=alt.X("满意度等级:N", title="满意度等级", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("评论数量:Q", title="评论数量"),
    color=alt.Color("品牌:N", title="品牌", scale=alt.Scale(domain=["真维斯", "优衣库"], range=["blue", "orange"]))
)
st.markdown("### 满意度等级分布对比")
st.altair_chart(satisfaction_distribution_chart.interactive())

# ===================== 热门颜色Top10对比可视化模块 ====================
# 合并热门颜色数据
colors_j_top_df = pd.DataFrame({"颜色": list(colors_j_top.keys()), "评论数量": list(colors_j_top.values())})
colors_j_top_df["品牌"] = "真维斯"  # 添加品牌字段

colors_u_top_df = pd.DataFrame({"颜色": list(colors_u_top.keys()), "评论数量": list(colors_u_top.values())})
colors_u_top_df["品牌"] = "优衣库"  # 添加品牌字段

# 创建热门颜色图表
colors_j_top_chart = alt.Chart(colors_j_top_df).mark_bar().encode(
    x=alt.X("颜色:N", title="颜色", sort="-y"),
    y=alt.Y("评论数量:Q", title="评论数量"),
    color=alt.Color("品牌:N", title="品牌", scale=alt.Scale(domain=["真维斯", "优衣库"], range=["blue", "orange"]))
).properties(
    title="真维斯 - 热门颜色 Top10",
    width=275  
)

colors_u_top_chart = alt.Chart(colors_u_top_df).mark_bar().encode(
    x=alt.X("颜色:N", title="颜色", sort="-y"),
    y=alt.Y("评论数量:Q", title="评论数量"),
    color=alt.Color("品牌:N", title="品牌", scale=alt.Scale(domain=["真维斯", "优衣库"], range=["blue", "orange"]))
).properties(
    title="优衣库 - 热门颜色 Top10",
    width=275  
)

# 将热门颜色图表并排显示
colors_top_chart = alt.hconcat(colors_j_top_chart, colors_u_top_chart).resolve_scale(x='independent')
st.markdown("### 热门颜色 Top10 对比")
st.altair_chart(colors_top_chart.interactive())

# ===================== 热门尺码Top10对比可视化模块 ====================
# 合并热门尺码数据
sizes_j_top_df = pd.DataFrame({"尺码": list(sizes_j_top.keys()), "评论数量": list(sizes_j_top.values())})
sizes_j_top_df["品牌"] = "真维斯"  # 添加品牌字段

sizes_u_top_df = pd.DataFrame({"尺码": list(sizes_u_top.keys()), "评论数量": list(sizes_u_top.values())})
sizes_u_top_df["品牌"] = "优衣库"  # 添加品牌字段

# 创建热门尺码图表
sizes_j_top_chart = alt.Chart(sizes_j_top_df).mark_bar().encode(
    x=alt.X("尺码:N", title="尺码", sort="-y", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("评论数量:Q", title="评论数量"),
    color=alt.Color("品牌:N", title="品牌", scale=alt.Scale(domain=["真维斯", "优衣库"], range=["blue", "orange"]))
).properties(
    title="真维斯 - 热门尺码 Top10",
    width=275
)

sizes_u_top_chart = alt.Chart(sizes_u_top_df).mark_bar().encode(
    x=alt.X("尺码:N", title="尺码", sort="-y"),
    y=alt.Y("评论数量:Q", title="评论数量"),
    color=alt.Color("品牌:N", title="品牌", scale=alt.Scale(domain=["真维斯", "优衣库"], range=["blue", "orange"]))
).properties(
    title="优衣库 - 热门尺码 Top10",
    width=275
)

# 将热门尺码图表并排显示
sizes_top_chart = alt.hconcat(sizes_j_top_chart, sizes_u_top_chart).resolve_scale(x='independent')
st.markdown("### 热门尺码 Top10 对比")
st.altair_chart(sizes_top_chart.interactive())

st.button("重新加载")
