import pandas as pd

# 读取文件
excel_file = pd.ExcelFile('评论_真维斯.xls')

# 获取所有表名
sheet_names = excel_file.sheet_names

# 获取指定工作表中的数据
df = excel_file.parse('Sheet1')

# 查看数据的基本信息
print('数据基本信息：')
df.info()

# 查看数据集行数和列数
rows, columns = df.shape

if rows < 100 and columns < 20:
    # 短表数据（行数少于100且列数少于20）查看全量数据信息
    print('数据全部内容信息：')
    print(df.to_csv(sep='\t', na_rep='nan'))
else:
    # 长表数据查看数据前几行信息
    print('数据前几行内容信息：')
    print(df.head().to_csv(sep='\t', na_rep='nan'))
    
# 检查重复值
print('重复值数量：', df.duplicated().sum())

# 删除全空列
df = df.dropna(axis=1, how='all')
print(f"删除了 {columns - df.shape[1]} 个全空列")

# 删除userInfo列
if 'userInfo' in df.columns:
    df = df.drop(columns=['userInfo'])
    print('已删除userInfo列')

# 处理缺失值
# 填充object类型缺失值(除了Q列和AL列)
object_columns = df.select_dtypes(include='object').columns
object_columns = object_columns.drop(['displayRatePic', 'tmallSweetPic'], errors='ignore')
df[object_columns] = df[object_columns].fillna('')

# 填充数值类型缺失值为0
numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
df[numeric_columns] = df[numeric_columns].fillna(0)

# 使用前向填充法处理Q列(displayRatePic)
df['displayRatePic'] = df['displayRatePic'].fillna(method='ffill')

# 使用后向填充法处理AL列(tmallSweetPic)
df['tmallSweetPic'] = df['tmallSweetPic'].fillna(method='bfill')

# 转换 rateDate 列的数据类型为日期时间类型
df['rateDate'] = pd.to_datetime(df['rateDate'])

# -----------------------------------------------------
# ✅ 统计每个商品编号的评论数量（近似销售量）
# -----------------------------------------------------
item_sales = df['_itemnumber_'].value_counts().reset_index()
item_sales.columns = ['_itemnumber_', 'comment_count']

# -----------------------------------------------------
# ✅ 方法 3：按销量估计价格
# -----------------------------------------------------
def estimate_by_sales(sales_count):
    if sales_count >= 200:
        return 145  # 热卖款
    elif sales_count >= 100:
        return 175
    else:
        return 240

item_sales['estimated_price_by_sales'] = item_sales['comment_count'].apply(estimate_by_sales)

# 将清洗后的数据保存为 xlsx 文件
xlsx_path = '评论_真维斯_清洗后.xlsx'
df.to_excel(xlsx_path, index=False)
# 2. 保存商品销售统计表，含估计价格
item_sales.to_excel('真维斯_商品销售统计.xlsx', index=False)
print("✅ 已成功生成并保存包含估计价格的销售统计文件！")
