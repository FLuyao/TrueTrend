import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import re

class BrandSalesAnalyzer:
    """竞争对比分析工具：完成销售汇总、趋势、热销、满意度与 SKU 分布图。"""

    # -------------------------------------------------- 初始化 -------------------------------------------------- #
    def __init__(self, jeanswest_reviews_path, uniqlo_reviews_path, jeanswest_sales_path):
        # 载入数据
        self.jeanswest_reviews = pd.read_excel(jeanswest_reviews_path)
        self.uniqlo_reviews   = pd.read_excel(uniqlo_reviews_path)
        self.jeanswest_sales  = pd.read_excel(jeanswest_sales_path)

        # 统一列名：去除空格/引号并转小写
        self._clean_cols(self.jeanswest_reviews)
        self._clean_cols(self.uniqlo_reviews)
        self._clean_cols(self.jeanswest_sales)

        # 兼容不同文件版本的商品编号列
        self._ensure_itemnumber_column(self.uniqlo_reviews)
        self._ensure_itemnumber_column(self.jeanswest_sales, source_col="_itemnumber_")

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

        jw_total_sales   = self.jeanswest_sales["comment_count"].sum()
        jw_total_revenue = (self.jeanswest_sales["comment_count"] * self.jeanswest_sales["estimated_price_by_sales"]).sum()
        uq_total_sales   = uq_summary["comment_count"].sum()
        uq_total_revenue = uq_summary["estimated_price_by_sales"].sum()

        return pd.DataFrame({
            "品牌": ["真维斯", "优衣库"],
            "销售量（估算）": [jw_total_sales, uq_total_sales],
            "销售额（估算, 元）": [jw_total_revenue, uq_total_revenue]
        })

    # -------------------------------------------------- 可视化 -------------------------------------------------- #
    def plot_monthly_trends(self):
        self.preprocess()
        jw_monthly = self.jeanswest_reviews["ratedate"].dt.to_period("M").value_counts().sort_index()
        uq_monthly = self.uniqlo_reviews["ratedate_dt"].dt.to_period("M").value_counts().sort_index()
        all_months = sorted(set(jw_monthly.index).union(uq_monthly.index))
        jw_monthly = jw_monthly.reindex(all_months, fill_value=0)
        uq_monthly = uq_monthly.reindex(all_months, fill_value=0)

        plt.figure(figsize=(12, 6))
        plt.plot(jw_monthly.index.to_timestamp(), jw_monthly.values, label="真维斯")
        plt.plot(uq_monthly.index.to_timestamp(), uq_monthly.values, label="优衣库")
        plt.title("月度评论量趋势对比（近似销售量）")
        plt.xlabel("时间")
        plt.ylabel("评论数量")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_top_items(self, top_n=10):
        self._ensure_itemnumber_column(self.uniqlo_reviews)
        uq_summary = self.uniqlo_reviews["itemnumber"].value_counts().reset_index()
        uq_summary.columns = ["itemnumber", "comment_count"]
        top_uq = uq_summary.nlargest(top_n, "comment_count")

        self._ensure_itemnumber_column(self.jeanswest_sales, source_col="_itemnumber_")
        top_jw = self.jeanswest_sales.nlargest(top_n, "comment_count")

        plt.figure(figsize=(14, 6))
        plt.subplot(1, 2, 1)
        plt.bar(top_jw["itemnumber"].astype(str), top_jw["comment_count"])
        plt.title(f"真维斯 热销商品 Top{top_n}")
        plt.xticks(rotation=90)

        plt.subplot(1, 2, 2)
        plt.bar(top_uq["itemnumber"].astype(str), top_uq["comment_count"])
        plt.title(f"优衣库 热销商品 Top{top_n}")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()

    def plot_satisfaction_distribution(self):
        jw = self.jeanswest_reviews["tamllsweetlevel"].value_counts().sort_index()
        uq = self.uniqlo_reviews["attr_tmall_vip_level"].value_counts().sort_index()
        levels = sorted(set(jw.index).union(uq.index))
        jw = jw.reindex(levels, fill_value=0)
        uq = uq.reindex(levels, fill_value=0)

        plt.figure(figsize=(10, 6))
        idx = range(len(levels))
        bw = 0.35
        plt.bar(idx, jw.values, bw, label="真维斯")
        plt.bar([i + bw for i in idx], uq.values, bw, label="优衣库")
        plt.xlabel("满意度等级")
        plt.ylabel("评论数")
        plt.title("满意度等级分布对比")
        plt.xticks([i + bw / 2 for i in idx], levels)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_sku_distributions(self):
        colors_j, sizes_j = self._extract_color_size(self.jeanswest_reviews.get("auctionsku", pd.Series(dtype=str)))
        colors_u, sizes_u = self._extract_color_size(self.uniqlo_reviews.get("attr_sku", pd.Series(dtype=str)))

        colors_j_top = dict(Counter(colors_j).most_common(10))
        colors_u_top = dict(Counter(colors_u).most_common(10))
        sizes_j_top  = dict(Counter(sizes_j).most_common(10))
        sizes_u_top  = dict(Counter(sizes_u).most_common(10))

        plt.figure(figsize=(14, 6))
        plt.subplot(1, 2, 1)
        plt.bar(colors_j_top.keys(), colors_j_top.values())
        plt.title("真维斯 - 热门颜色 Top10")
        plt.xticks(rotation=45)
        plt.subplot(1, 2, 2)
        plt.bar(colors_u_top.keys(), colors_u_top.values())
        plt.title("优衣库 - 热门颜色 Top10")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        plt.figure(figsize=(14, 6))
        plt.subplot(1, 2, 1)
        plt.bar(sizes_j_top.keys(), sizes_j_top.values())
        plt.title("真维斯 - 热门尺码 Top10")
        plt.xticks(rotation=45)
        plt.subplot(1, 2, 2)
        plt.bar(sizes_u_top.keys(), sizes_u_top.values())
        plt.title("优衣库 - 热门尺码 Top10")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

analyzer = BrandSalesAnalyzer("评论_真维斯_清洗后.xlsx", "reviews_uni_clean.xlsx", "真维斯_商品销售统计.xlsx")
analyzer.preprocess()
analyzer.compare_total_sales()
analyzer.plot_monthly_trends()
analyzer.plot_top_items()
analyzer.plot_satisfaction_distribution()
analyzer.plot_sku_distributions()