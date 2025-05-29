import pandas as pd
import streamlit as st

@st.cache_data
def get_sentiment_distribution():
    df_reviews = pd.read_excel("data/评论_真维斯_清洗后.xlsx")

    positive_words = ['好', '满意', '喜欢', '合适', '划算', '值得', '舒服', '惊喜', '便宜', '正品', '赞']
    negative_words = ['差', '失望', '难看', '不好', '退货', '质量问题', '不值', '做工差', '色差', '起球']

    def analyze_sentiment(text, positive_words, negative_words):
        if pd.isna(text) or text.strip() == '':
            return '中性'
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        if pos_count > 0 and neg_count == 0:
            return '好评'
        elif neg_count > 0 and pos_count == 0:
            return '差评'
        elif pos_count > neg_count:
            return '好评'
        elif neg_count > pos_count:
            return '差评'
        else:
            return '中性'

    df_reviews["情感分类"] = df_reviews["rateContent"].apply(lambda x: analyze_sentiment(x, positive_words, negative_words))

    sentiment_stats = df_reviews["情感分类"].value_counts()

    return  sentiment_stats





