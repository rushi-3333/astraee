import os
import joblib
import pandas as pd
import numpy as np
from django.conf import settings

class AEECFPredictor:
    """Base class for Attention-Enhanced Ensemble CatBoost Framework (AEECF) inference."""

    def __init__(self, model_folder_name, model_file_name):
        self.model_dir = os.path.join(settings.BASE_DIR, 'Model', model_folder_name)
        
        # Load artifacts
        self.model = joblib.load(os.path.join(self.model_dir, model_file_name))
        self.scaler = joblib.load(os.path.join(self.model_dir, 'scaler.pkl'))
        self.label_encoders = joblib.load(os.path.join(self.model_dir, 'label_encoders.pkl'))
        self.attention_weights = joblib.load(os.path.join(self.model_dir, 'attention_weights.pkl'))
        self.feature_columns = joblib.load(os.path.join(self.model_dir, 'feature_columns.pkl'))

    def predict(self, feature_dict):
        # 1. Initialize DataFrame with all feature columns initialized to default values
        df = pd.DataFrame([feature_dict])

        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0.0

        # 2. Categorical Encoding with fallback for unseen categories
        for col, encoder in self.label_encoders.items():
            if col in df.columns:
                val = str(df[col].iloc[0])
                if hasattr(encoder, 'classes_') and val in encoder.classes_:
                    df[col] = encoder.transform([val])[0]
                else:
                    df[col] = 0

        # 3. Identify numerical columns
        numerical_cols = [
            c for c in self.feature_columns 
            if c not in self.label_encoders
        ]

        # Ensure all required columns exist in exact order expected by Scaler
        df = df[self.feature_columns]

        # 4. Apply Feature Scaling on scaler's expected feature set
        try:
            if hasattr(self.scaler, 'feature_names_in_'):
                scaler_features = list(self.scaler.feature_names_in_)
                df[scaler_features] = self.scaler.transform(df[scaler_features])
            else:
                df[numerical_cols] = self.scaler.transform(df[numerical_cols])
        except Exception:
            # Fallback in case of custom scaler structures
            pass

        # 5. Apply Attention Weights
        for col in numerical_cols:
            if isinstance(self.attention_weights, dict) and col in self.attention_weights:
                df[col] = df[col] * self.attention_weights[col]

        # 6. Run Prediction
        prediction = self.model.predict(df)
        return max(0.0, float(prediction[0]))