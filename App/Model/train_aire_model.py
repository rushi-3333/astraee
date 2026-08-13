import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'user_interaction_rl_dataset.csv')
AIRE_MODEL_DIR = os.path.join(BASE_DIR, 'AIRE_model')

os.makedirs(AIRE_MODEL_DIR, exist_ok=True)

def train_aire():
    print("=" * 60)
    print("Training ASTRAE Intelligent Recommendation Engine (AIRE)")
    print("=" * 60)

    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] Dataset not found at {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip().str.lower()

    # 1. Derive Reward Signal
    clicked = df['clicked'] if 'clicked' in df.columns else pd.Series(1, index=df.index)
    converted = df['converted'] if 'converted' in df.columns else (df['booked'] if 'booked' in df.columns else pd.Series(1, index=df.index))
    savings = df['savings'] if 'savings' in df.columns else pd.Series(20.0, index=df.index)

    df['reward_score'] = (clicked * 10.0) + (converted * 50.0) + (savings * 0.2)

    # 2. Select Features
    cat_cols = ['category', 'platform']
    num_cols = ['final_price', 'rating', 'eta_mins', 'coupon_discount']

    for col in cat_cols + num_cols:
        if col not in df.columns:
            if col == 'category': df[col] = 'ride'
            elif col == 'platform': df[col] = 'Uber'
            elif col == 'final_price': df[col] = df.get('price', 100.0)
            elif col == 'rating': df[col] = df.get('user_rating', 4.2)
            elif col == 'eta_mins': df[col] = df.get('delivery_time', 20.0)
            elif col == 'coupon_discount': df[col] = df.get('discount', 0.0)

    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    scaler = StandardScaler()
    feature_cols = cat_cols + num_cols
    X = df[feature_cols].fillna(0)
    X[num_cols] = scaler.fit_transform(X[num_cols])
    y = df['reward_score']

    # 3. Fit Gradient Boosting Model
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X, y)

    # 4. Save Artifacts
    joblib.dump(model, os.path.join(AIRE_MODEL_DIR, 'aire_rl_model.pkl'))
    joblib.dump(scaler, os.path.join(AIRE_MODEL_DIR, 'aire_scaler.pkl'))
    joblib.dump(encoders, os.path.join(AIRE_MODEL_DIR, 'aire_encoders.pkl'))
    joblib.dump(feature_cols, os.path.join(AIRE_MODEL_DIR, 'aire_features.pkl'))

    print(f"[SUCCESS] AIRE model artifacts successfully saved to {AIRE_MODEL_DIR}\n")

if __name__ == '__main__':
    train_aire()