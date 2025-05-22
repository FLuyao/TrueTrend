# coding=utf-8
import pandas as pd
import numpy as np
import json, ast, re
from pandas import json_normalize


# 0. 读入原始数据
df = pd.read_excel(
    "reviews_uni.xls",
    dtype=str,                       # 先全部按字符串读入，后面再分列转类型
    na_values=["", "null", "NULL", "NaN"]
)

# 1. 基础清洗
# 去掉列名里的星号/首尾空格，统一 snake_case
def clean_colname(c):
    return re.sub(r"\*|\s+", "", c).strip().lower()

df.columns = [clean_colname(c) for c in df.columns]

dupe_cols = [c for c in ["ratecontent", "userid_encryption"] if c in df.columns]

if dupe_cols:                     # 至少有 1 个才去重
    df = df.drop_duplicates(subset=dupe_cols)
else:
    print("⚠️  去重跳过：ratecontent / userid_encryption 均不存在")

    
# 将 'true'/'false' → 布尔；若有缺失保持 NaN
bool_cols = ["alimallseller", "anony", "frommall", "frommemory"]
for col in bool_cols:
    df[col] = df[col].str.upper().map({"TRUE": True, "FALSE": False, "1":True, "0":False})

# 科学计数字符串 → 数值类型
num_cols = [
    "auctionprice","buycount","displayratesum","gmtcreatetime",
    "tradeid","displayusernumid"
]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 13 位毫秒时间戳（gmtcreatetime、tradeendtime 等）
ts_cols = ["gmtcreatetime", "tradeendtime"]
for col in ts_cols:
    df[col + "_dt"] = pd.to_datetime(df[col], unit="ms", errors="coerce")

# 普通日期字符串列
df["ratedate_dt"] = pd.to_datetime(df["ratedate"], errors="coerce")


# 2. 解析 & 展开嵌套 JSON / KV 字符串
def parse_pseudo_json(x):
    """把单引号、u'xxx' 形式转换成真正的 dict。失败时返回空 dict。"""
    if pd.isna(x) or not isinstance(x, str) or not x.strip():
        return {}
    try:
        # ast.literal_eval 允许单引号与 unicode 前缀
        return ast.literal_eval(x)
    except Exception:
        return {}

# 以 attributesmap 为例
attr_series = df["attributesmap"].map(parse_pseudo_json)

# 将 key/value 拆列，避免列过多：只留你关心的字段
KEYS_TO_KEEP = [
    "sku", "spuId", "leafCatId", "tmall_vip_level",
    "worth_score", "rate_order_worth", "rate_worth"
]
attr_df = json_normalize(attr_series).reindex(columns=KEYS_TO_KEEP)

# 列名加前缀避免冲突
attr_df = attr_df.add_prefix("attr_")

# 和主表横向拼接
df = pd.concat([df.drop(columns=["attributesmap"]), attr_df], axis=1)

# 3. 文本标准化（示例：ratecontent 去掉换行、首尾空格）
df["ratecontent"] = (
    df["ratecontent"]
    .fillna("")
    .str.replace(r"\s+", " ", regex=True)   # 连续空白变单空格
    .str.strip()
)

# 4. 保存清洗结果
df.to_excel(
    "reviews_uni_clean.xlsx",
    index=False,
    engine="openpyxl"      # 或 "xlsxwriter"，两者二选一都行
)

print("✅ 数据清洗完成，保存为  reviews_uni_clean.xlsx")