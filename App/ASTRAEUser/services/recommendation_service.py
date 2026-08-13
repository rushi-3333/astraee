import os
import joblib
import pandas as pd
import numpy as np
from django.conf import settings

AIRE_MODEL_DIR = os.path.join(settings.BASE_DIR, 'Model', 'AIRE_model')

_aire_model = None
_aire_scaler = None
_aire_encoders = None
_aire_features = None

def _load_aire_artifacts():
    global _aire_model, _aire_scaler, _aire_encoders, _aire_features
    if _aire_model is None:
        model_path = os.path.join(AIRE_MODEL_DIR, 'aire_rl_model.pkl')
        if os.path.exists(model_path):
            _aire_model = joblib.load(model_path)
            _aire_scaler = joblib.load(os.path.join(AIRE_MODEL_DIR, 'aire_scaler.pkl'))
            _aire_encoders = joblib.load(os.path.join(AIRE_MODEL_DIR, 'aire_encoders.pkl'))
            _aire_features = joblib.load(os.path.join(AIRE_MODEL_DIR, 'aire_features.pkl'))

def rank_candidates_with_aire(category, candidates):
    """
    Evaluates candidate platform options using AIRE RL model scoring.
    Falls back to weighted heuristic scoring if ML artifacts are missing.
    """
    if not candidates:
        return []

    _load_aire_artifacts()

    prices = [c['final_price'] for c in candidates]
    max_price = max(prices) if prices else 1.0
    min_price = min(prices) if prices else 0.0

    scored_candidates = []

    for candidate in candidates:
        # Calculate Savings Score (100 = cheapest candidate)
        price_range = max(1.0, max_price - min_price)
        savings_score = int(round(100.0 * (1.0 - ((candidate['final_price'] - min_price) / price_range))))
        savings_score = max(50, min(100, savings_score))

        if _aire_model is not None:
            try:
                feature_dict = {
                    'category': category,
                    'platform': candidate['platform'],
                    'final_price': float(candidate['final_price']),
                    'rating': float(candidate['rating']),
                    'eta_mins': float(candidate['eta_mins']),
                    'coupon_discount': float(candidate.get('coupon_discount', 0.0))
                }
                df = pd.DataFrame([feature_dict])

                for col, encoder in _aire_encoders.items():
                    val = str(df[col].iloc[0])
                    df[col] = encoder.transform([val])[0] if hasattr(encoder, 'classes_') and val in encoder.classes_ else 0

                num_cols = ['final_price', 'rating', 'eta_mins', 'coupon_discount']
                df[num_cols] = _aire_scaler.transform(df[num_cols])
                df = df[_aire_features]

                raw_score = float(_aire_model.predict(df)[0])
                aire_score = min(100, max(60, int(raw_score)))
            except Exception:
                aire_score = savings_score
        else:
            # Fallback heuristic calculation
            aire_score = savings_score

        candidate_copy = dict(candidate)
        candidate_copy['savings_score'] = savings_score
        candidate_copy['aire_score'] = aire_score
        scored_candidates.append(candidate_copy)

    # Rank by AIRE Score descending
    return sorted(scored_candidates, key=lambda x: x['aire_score'], reverse=True)