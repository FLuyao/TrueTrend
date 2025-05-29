import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from analysis.真维斯销售量短期预测 import predict_and_analyze
from analysis.真维斯销售量长期预测 import long_term_predict_and_analyze
from analysis.真维斯16年双十一预测 import predict_sales_11

st.set_page_config(page_title="预测分析", page_icon="📈")

st.markdown("# 预测分析")
st.sidebar.header("预测分析")
st.write(
    """本页面展示了真维斯品牌的短期销售预测、
    长期销售预测以及2016年双十一销售预测等信息。
    通过这些预测图表，你可以了解未来的销售趋势和预期销量。"""
)

# ===================== 销售短期预测可视化模块 ====================
# 加载数据
daily_comments, pred_index, predictions, result_df = predict_and_analyze()

# 将结果转换为DataFrame
chart_data = pd.DataFrame({
    '日期': daily_comments.index.to_list() + pred_index.to_list(),
    '销量': daily_comments.to_list() + predictions,
    '类型': ['实际数据'] * len(daily_comments) + ['预测数据'] * len(predictions)
})

st.markdown("### 销售量短期预测")
st.altair_chart(
    alt.Chart(chart_data).mark_line().encode(
        x=alt.X('日期:T', title='日期'),
        y=alt.Y('销量:Q', title='销量'),
        color=alt.Color('类型:N', title='数据类型')
    ).interactive()
)

st.dataframe(result_df)

# 在左侧sidebar中统计信息
with st.sidebar:
    st.markdown("### 提示")
    st.markdown(f"短期预测: **{pred_index[0].strftime('%Y-%m-%d')}——{pred_index[-1].strftime('%Y-%m-%d')}**")

# ===================== 销售长期预测可视化模块 ====================
# 加载数据
daily_comments, future_dates, long_term_predictions, forecast_df = long_term_predict_and_analyze()

# 将结果转换为DataFrame
long_term_chart_data = pd.DataFrame({
    '日期': daily_comments.index.to_list() + future_dates.to_list(),
    '销量': daily_comments.to_list() + long_term_predictions,
    '类型': ['实际数据'] * len(daily_comments) + ['预测数据'] * len(long_term_predictions)
})

st.markdown("### 销售量长期预测")
st.altair_chart(
    alt.Chart(long_term_chart_data).mark_line().encode(
        x=alt.X('日期:T', title='日期'),
        y=alt.Y('销量:Q', title='销量'),
        color=alt.Color('类型:N', title='数据类型')
    ).interactive()
)

st.dataframe(forecast_df)

# 在左侧sidebar中统计信息
with st.sidebar:
    st.markdown(f"长期预测: **{future_dates[0].strftime('%Y-%m-%d')}——{future_dates[-1].strftime('%Y-%m-%d')}**")

# ===================== 16年双十一销售预测可视化模块 ====================
# 加载数据
days, daily_pred, result = predict_sales_11()

# 将结果转换为DataFrame
daily_11_df = pd.DataFrame({
    '日期': [f"2016-11-{day:02d}" for day in days],
    '销量': daily_pred.values,
    '类型': ['预测数据'] * len(days)
})

# 使用Altair绘制图表
st.markdown("### 2016年11月每日销量预测（双十一预测）")
st.altair_chart(
    alt.Chart(daily_11_df).mark_line().encode(
        x=alt.X('日期:T', title='日期'),
        y=alt.Y('销量:Q', title='销量'),
        color=alt.Color('类型:N', title='数据类型')
    ).interactive()
)

st.dataframe(result)

st.button("重新加载")