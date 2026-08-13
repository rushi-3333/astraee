from datetime import datetime
from .prediction_base import AEECFPredictor

_food_predictor = None

def get_food_predictor():
    global _food_predictor
    if _food_predictor is None:
        _food_predictor = AEECFPredictor('Food_model', 'aeecf_food_catboost_model.pkl')
    return _food_predictor

def predict_food_price(metadata):
    now = datetime.now()
    predictor = get_food_predictor()

    food_price = float(metadata.get('food_price', 200.0))
    coupon_discount = float(metadata.get('coupon_discount', 0.0))
    cashback = float(metadata.get('cashback', 0.0))

    feature_dict = {
        'platform': metadata.get('platform', 'Swiggy'),
        'restaurant_name': metadata.get('restaurant_name', 'Generic'),
        'food_item': metadata.get('food_item', 'Item'),
        'category': metadata.get('category', 'Main Course'),
        'food_price': food_price,
        'delivery_fee': float(metadata.get('delivery_fee', 30.0)),
        'packaging_fee': float(metadata.get('packaging_fee', 10.0)),
        'tax_amount': float(metadata.get('tax_amount', 15.0)),
        'delivery_time_min': int(metadata.get('delivery_time_min', 30)),
        'restaurant_rating': float(metadata.get('restaurant_rating', 4.2)),
        'review_count': int(metadata.get('review_count', 100)),
        'available_coupon': int(metadata.get('available_coupon', 1 if coupon_discount > 0 else 0)),
        'coupon_discount': coupon_discount,
        'cashback': cashback,
        'effective_discount': coupon_discount + cashback,
        'demand_level': metadata.get('demand_level', 'Medium'),
        'demand_score': 2 if metadata.get('demand_level') == 'High' else 1,
        'time_slot': metadata.get('time_slot', 'Dinner'),
        'peak_meal_time': 1 if metadata.get('time_slot') in ['Lunch', 'Dinner'] else 0,
        'day_of_week': metadata.get('day_of_week', now.strftime('%A')),
        'festival_indicator': int(metadata.get('festival_indicator', 0)),
        'month': now.month,
        'day': now.day,
        'is_weekend': 1 if now.weekday() >= 5 else 0
    }

    return round(predictor.predict(feature_dict), 2)