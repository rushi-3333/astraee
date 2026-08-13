from datetime import datetime
from .prediction_base import get_cached_predictor


def get_ride_predictor():
    return get_cached_predictor('ride', 'Ride_model', 'aeecf_catboost_model.pkl')


def predict_ride_price(metadata):
    now = datetime.now()
    predictor = get_ride_predictor()
    fallback_price = float(metadata.get('fare_price', metadata.get('base_fare', 150.0)))

    if predictor is None:
        return round(fallback_price, 2)

    feature_dict = {
        'platform': metadata.get('platform', 'Uber'),
        'route': f"{metadata.get('pickup_location', '')} -> {metadata.get('destination', '')}",
        'distance_km': float(metadata.get('distance_km', 10.0)),
        'estimated_duration_min': int(metadata.get('estimated_duration_min', 20)),
        'vehicle_type': metadata.get('vehicle_type', 'Car'),
        'base_fare': float(metadata.get('base_fare', 100.0)),
        'surge_multiplier': float(metadata.get('surge_multiplier', 1.0)),
        'estimated_arrival_min': int(metadata.get('estimated_arrival_min', 5)),
        'driver_rating': float(metadata.get('driver_rating', 4.5)),
        'available_coupon': int(metadata.get('available_coupon', 0)),
        'coupon_discount': float(metadata.get('coupon_discount', 0.0)),
        'cashback': float(metadata.get('cashback', 0.0)),
        'demand_level': metadata.get('demand_level', 'Medium'),
        'weather_condition': metadata.get('weather_condition', 'Clear'),
        'traffic_level': metadata.get('traffic_level', 'Normal'),
        'day_of_week': metadata.get('day_of_week', now.strftime('%A')),
        'hour_of_day': int(metadata.get('hour_of_day', now.hour)),
        'festival_indicator': int(metadata.get('festival_indicator', 0)),
        'month': now.month,
        'day': now.day,
        'is_weekend': 1 if now.weekday() >= 5 else 0,
        'is_peak_hour': 1 if now.hour in [8, 9, 10, 17, 18, 19, 20] else 0,
        'demand_score': 3
    }

    try:
        return round(predictor.predict(feature_dict), 2)
    except Exception:
        return round(fallback_price, 2)