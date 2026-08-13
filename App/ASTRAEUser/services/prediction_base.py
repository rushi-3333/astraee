import os
import joblib
import pandas as pd
from django.conf import settings

_predictor_cache = {}


class AEECFPredictor:
    """Base class for Attention-Enhanced Ensemble CatBoost Framework (AEECF) inference."""

    def __init__(self, model_folder_name, model_file_name):
        self.model_dir = os.path.join(settings.BASE_DIR, 'Model', model_folder_name)
        self._ready = False
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.attention_weights = None
        self.feature_columns = None

        required = [
            model_file_name,
            'scaler.pkl',
            'label_encoders.pkl',
            'attention_weights.pkl',
            'feature_columns.pkl',
        ]
        paths = [os.path.join(self.model_dir, f) for f in required]
        if not all(os.path.exists(p) for p in paths):
            return

        try:
            self.model = joblib.load(paths[0])
            self.scaler = joblib.load(paths[1])
            self.label_encoders = joblib.load(paths[2])
            self.attention_weights = joblib.load(paths[3])
            self.feature_columns = joblib.load(paths[4])
            self._ready = True
        except Exception:
            self._ready = False

    @property
    def is_ready(self):
        return self._ready

    def predict(self, feature_dict):
        if not self._ready:
            raise RuntimeError('AEECF model artifacts are not available')

        df = pd.DataFrame([feature_dict])

        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0.0

        for col, encoder in self.label_encoders.items():
            if col in df.columns:
                val = str(df[col].iloc[0])
                if hasattr(encoder, 'classes_') and val in encoder.classes_:
                    df[col] = encoder.transform([val])[0]
                else:
                    df[col] = 0

        numerical_cols = [
            c for c in self.feature_columns
            if c not in self.label_encoders
        ]

        df = df[self.feature_columns]

        try:
            if hasattr(self.scaler, 'feature_names_in_'):
                scaler_features = list(self.scaler.feature_names_in_)
                df[scaler_features] = self.scaler.transform(df[scaler_features])
            else:
                df[numerical_cols] = self.scaler.transform(df[numerical_cols])
        except Exception:
            pass

        for col in numerical_cols:
            if isinstance(self.attention_weights, dict) and col in self.attention_weights:
                df[col] = df[col] * self.attention_weights[col]

        prediction = self.model.predict(df)
        return max(0.0, float(prediction[0]))


def get_cached_predictor(cache_key, model_folder_name, model_file_name):
    """Load predictor once; return None when artifacts are missing."""
    if cache_key in _predictor_cache:
        return _predictor_cache[cache_key]
    try:
        predictor = AEECFPredictor(model_folder_name, model_file_name)
        _predictor_cache[cache_key] = predictor if predictor.is_ready else None
    except Exception:
        _predictor_cache[cache_key] = None
    return _predictor_cache[cache_key]
