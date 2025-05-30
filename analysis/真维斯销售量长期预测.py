import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

# 1. 加载数据并提取波动特征
def load_data():
    df = pd.read_excel('data/评论_真维斯_清洗后.xlsx')
    df['rateDate'] = pd.to_datetime(df['rateDate'])
    daily_comments = df.groupby(df['rateDate'].dt.date).size()
    daily_comments.index = pd.to_datetime(daily_comments.index)
    daily_comments = daily_comments.asfreq('D').fillna(0)
    return daily_comments

# 2. 构建增强波动性的特征
def create_volatile_features(data):
    return pd.DataFrame({
        'day_volatility': data.rolling(3).std().fillna(0) * 2,  
        'lag1': data.shift(1).fillna(0),
        'lag3': data.shift(3).fillna(0),
        'lag7': data.shift(7).fillna(0),
        'spike_indicator': (data.diff().abs() > data.mean()).astype(int).shift(1).fillna(0)
    })

# 3. 训练拟合的模型
def train_model(data_clean):
    train_data = data_clean.loc['2015-11-01':'2016-01-31']
    X_train, y_train = train_data.iloc[:, :-1], train_data.iloc[:, -1]
    model = GradientBoostingRegressor(
        n_estimators=50,
        max_depth=5,
        learning_rate=0.3,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model
# 4. 生成预测
def generate_long_term_predictions(model, daily_comments):
    future_dates = pd.date_range('2016-02-01', periods=90)
    X_future = pd.DataFrame(index=future_dates)
    predictions = []
    history = daily_comments['2015-12-01':'2016-01-31'].tolist()

    for i in range(90):
        volatility = daily_comments.std() * 1.0
        random_shock = np.random.normal(0, volatility)
    
        X_future.loc[future_dates[i], 'day_volatility'] = volatility
        X_future.loc[future_dates[i], 'lag1'] = predictions[i-1] if i>0 else history[-1]
        X_future.loc[future_dates[i], 'lag3'] = predictions[i-3] if i>=3 else history[-(3-i)]
        X_future.loc[future_dates[i], 'lag7'] = predictions[i-7] if i>=7 else history[-(7-i)]
        X_future.loc[future_dates[i], 'spike_indicator'] = 1 if np.random.rand() > 0.7 else 0
    
        pred = model.predict(X_future.iloc[[i]])[0] + random_shock
        predictions.append(max(0, pred))  # 保持非负

    return future_dates, predictions

# 封装长期预测分析
def long_term_predict_and_analyze():
    daily_comments = load_data()
    X = create_volatile_features(daily_comments)
    y = daily_comments
    data_clean = pd.concat([X, y], axis=1).dropna()
    model = train_model(data_clean)
    future_dates, predictions = generate_long_term_predictions(model, daily_comments)
    
    # 保存预测结果
    forecast_df = pd.DataFrame({
        '日期': future_dates,
        '预测销量': predictions
    })
    
    return daily_comments, future_dates, predictions, forecast_df
