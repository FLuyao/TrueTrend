import pandas as pd
from collections import Counter
import re


class BrandSalesAnalyzer:
    """竞争对比分析工具：完成销售汇总、趋势、热销、满意度与 SKU 分布图。"""

    # -------------------------------------------------- 初始化 -------------------------------------------------- #
    def __init__(self, jeanswest_reviews_path, uniqlo_reviews_path, jeanswest_sales_path):
        # 载入数据
        self.jeanswest_reviews = pd.read_excel(jeanswest_reviews_path)
        self.uniqlo_reviews = pd.read_excel(uniqlo_reviews_path)
        self.jeanswest_sales = pd.read_excel(jeanswest_sales_path)

        # 统一列名：去除空格/引号并转小写
        self._clean_cols(self.jeanswest_reviews)
        self._clean_cols(self.uniqlo_reviews)
        self._clean_cols(self.jeanswest_sales)

        # 兼容不同文件版本的商品编号列
        self._ensure_itemnumber_column(self.uniqlo_reviews)
        self._ensure_itemnumber_column(self.jeanswest_sales, source_col="_itemnumber_")


    def extract_color_size(self, series):
        """
        兼容两种格式：
        · 颜色:酒红; 尺码:M
        · 颜色分类#3B14 玛瑙红色#3A尺码#3B160/88A/L
        """
        colors, sizes = [], []

        for txt in series.dropna().astype(str):
            # ---------- 颜色 ----------
            # 先匹配 '颜色分类#XXXX 空格 颜色名'
            m_color = re.search(r'颜色(?:分类)?[^#]*#\w+\s*([^\#;:\s]+)', txt)
            # 再匹配 '颜色[:：] 颜色名'
            if not m_color:
                m_color = re.search(r'颜色[:：]?\s*([^\s;，#]+)', txt)
            # 备份英文 Color
            if not m_color:
                m_color = re.search(r'color[^#:：;]*[:\s]*([^\d#/;:\s]+)', txt, re.I)
            if m_color:
                colors.append(m_color.group(1).strip())

            # ---------- 尺码 ----------
            # 匹配 '尺码#XXXX 空格 尺码值'
            m_size = re.search(r'尺码[^#;:\s]*#\w+\s*([^\#;:\s]+)', txt)
            # 匹配 '尺码[:：] 尺码值'
            if not m_size:
                m_size = re.search(r'尺码[:：]?\s*([^\s;，#]+)', txt)
            # 备份英文 Size
            if not m_size:
                m_size = re.search(r'size[^#:：;]*[:\s]*([A-Za-z0-9/XL\-]+)', txt, re.I)
            if m_size:
                sizes.append(m_size.group(1).strip())

        return Counter(colors), Counter(sizes)


    # --------------------------------------------- 内部工具 -------------------------------------------------- #
    @staticmethod
    def _clean_cols(df):
        """将列名统一小写，并去掉首尾空格及引号"""
        df.columns = [c.strip().lower().strip("'\"") for c in df.columns]


    @staticmethod
    def _ensure_itemnumber_column(df, source_col="itemnumber"):
        """如果 df 中没有 'itemnumber' 列，则尝试从候选列中重命名复制"""
        if "itemnumber" in df.columns:
            return
        # 候选列名（含常见引号、下划线写法）
        candidates = [source_col, "_itemnumber_", "item_number", "itemnumid", "aucnumid",
                      "'itemnumber'", "\"itemnumber\""]
        for cand in candidates:
            if cand in df.columns:
                df.rename(columns={cand: "itemnumber"}, inplace=True)
                return
        raise KeyError("未找到商品编号列，请检查 Excel 列名 (itemnumber 或 _itemnumber_)。")


    @staticmethod
    def _extract_color_size(sku_series):
        """从 sku 文本中提取颜色与尺码，返回 Counter 统计"""
        colors, sizes = [], []
        pattern = re.compile(r"颜色[:：]?([^;，\s]+)[;，\s]+尺码[:：]?([^;，\s]+)")
        for val in sku_series.dropna():
            for color, size in pattern.findall(str(val)):
                colors.append(color.strip())
                sizes.append(size.strip())
        return Counter(colors), Counter(sizes)


    # -------------------------------------------------- 预处理 -------------------------------------------------- #
    def preprocess(self):
        if "ratedate" in self.jeanswest_reviews.columns:
            self.jeanswest_reviews["ratedate"] = pd.to_datetime(self.jeanswest_reviews["ratedate"], errors="coerce")
        if "ratedate_dt" in self.uniqlo_reviews.columns:
            self.uniqlo_reviews["ratedate_dt"] = pd.to_datetime(self.uniqlo_reviews["ratedate_dt"], errors="coerce")


    # -------------------------------------------------- 汇总 -------------------------------------------------- #
    def compare_total_sales(self, price_assumption=145):
        """返回两个品牌的销售量与销售额汇总 DataFrame"""
        self._ensure_itemnumber_column(self.uniqlo_reviews)  # 再次确保
        uq_summary = self.uniqlo_reviews["itemnumber"].value_counts().reset_index()
        uq_summary.columns = ["itemnumber", "comment_count"]
        uq_summary["estimated_price_by_sales"] = uq_summary["comment_count"] * price_assumption

        jw_total_sales = self.jeanswest_sales["comment_count"].sum()
        jw_total_revenue = (self.jeanswest_sales["comment_count"] * self.jeanswest_sales["estimated_price_by_sales"]).sum()
        uq_total_sales = uq_summary["comment_count"].sum()
        uq_total_revenue = uq_summary["estimated_price_by_sales"].sum()

        return pd.DataFrame({
            "品牌": ["真维斯", "优衣库"],
            "销售量（估算）": [jw_total_sales, uq_total_sales],
            "销售额（估算, 元）": [jw_total_revenue, uq_total_revenue]
        })


    def get_monthly_trends_data(self):
        self.preprocess()
        jw_monthly = self.jeanswest_reviews["ratedate"].dt.to_period("M").value_counts().sort_index()
        uq_monthly = self.uniqlo_reviews["ratedate_dt"].dt.to_period("M").value_counts().sort_index()
        all_months = sorted(set(jw_monthly.index).union(uq_monthly.index))
        jw_monthly = jw_monthly.reindex(all_months, fill_value=0)
        uq_monthly = uq_monthly.reindex(all_months, fill_value=0)

        return jw_monthly.index.to_timestamp(), jw_monthly.values, uq_monthly.values


    def get_top_items_data(self, top_n=10):
        self._ensure_itemnumber_column(self.uniqlo_reviews)
        uq_summary = self.uniqlo_reviews["itemnumber"].value_counts().reset_index()
        uq_summary.columns = ["itemnumber", "comment_count"]
        top_uq = uq_summary.nlargest(top_n, "comment_count")

        self._ensure_itemnumber_column(self.jeanswest_sales, source_col="_itemnumber_")
        top_jw = self.jeanswest_sales.nlargest(top_n, "comment_count")

        return top_jw["itemnumber"].astype(str), top_jw["comment_count"], top_uq["itemnumber"].astype(int).astype(str), top_uq["comment_count"]


    def get_satisfaction_distribution_data(self):
        jw = self.jeanswest_reviews["tamllsweetlevel"].value_counts().sort_index()
        uq = self.uniqlo_reviews["attr_tmall_vip_level"].value_counts().sort_index()
        levels = sorted(set(jw.index).union(uq.index))
        jw = jw.reindex(levels, fill_value=0)
        uq = uq.reindex(levels, fill_value=0)

        return levels, jw.values, uq.values


    def get_sku_distributions_data(self):
        colors_j, sizes_j = self._extract_color_size(self.jeanswest_reviews.get("auctionsku", pd.Series(dtype=str)))
        colors_u, sizes_u = self.extract_color_size(self.uniqlo_reviews.get("attr_sku", pd.Series(dtype=str)))

        colors_j_top = dict(Counter(colors_j).most_common(10))
        colors_u_top = dict(Counter(colors_u).most_common(10))
        sizes_j_top = dict(Counter(sizes_j).most_common(10))
        sizes_u_top = dict(Counter(sizes_u).most_common(10))

        return colors_j_top, colors_u_top, sizes_j_top, sizes_u_top



