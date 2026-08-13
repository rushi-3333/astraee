from datetime import datetime
from .prediction_base import AEECFPredictor

_medicine_predictor = None

def get_medicine_predictor():
    global _medicine_predictor
    if _medicine_predictor is None:
        _medicine_predictor = AEECFPredictor('medicine_model', 'aeecf_medicine_catboost_model.pkl')
    return _medicine_predictor

def predict_medicine_price(metadata):
    now = datetime.now()
    predictor = get_medicine_predictor()

    mrp = float(metadata.get('mrp', 100.0))
    selling_price = float(metadata.get('selling_price', 90.0))
    coupon_discount = float(metadata.get('coupon_discount', 0.0))
    cashback = float(metadata.get('cashback', 0.0))

    feature_dict = {
        'platform': metadata.get('platform', 'Netmeds'),
        'medicine_name': metadata.get('medicine_name', 'Medicine'),
        'manufacturer': metadata.get('manufacturer', 'Pharma'),
        'composition': metadata.get('composition', 'Salt'),
        'pack_size': metadata.get('pack_size', '10 tablets'),
        'mrp': mrp,
        'selling_price': selling_price,
        'discount_percentage': float(metadata.get('discount_percentage', 10.0)),
        'coupon_discount': coupon_discount,
        'cashback': cashback,
        'effective_discount': (mrp - selling_price) + coupon_discount + cashback,
        'total_savings': (mrp - selling_price) + coupon_discount + cashback,
        'delivery_time_hours': float(metadata.get('delivery_time_hours', 24.0)),
        'platform_rating': float(metadata.get('platform_rating', 4.5)),
        'review_count': int(metadata.get('review_count', 100)),
        'stock_status': metadata.get('stock_status', 'In Stock'),
        'stock_score': 1 if metadata.get('stock_status') == 'In Stock' else 0,
        'availability_score': 1 if metadata.get('stock_status') == 'In Stock' else 0,
        'prescription_required': metadata.get('prescription_required', 'No'),
        'prescription_flag': 1 if metadata.get('prescription_required') == 'Yes' else 0,
        'day_of_week': metadata.get('day_of_week', now.strftime('%A')),
        'festival_indicator': int(metadata.get('festival_indicator', 0)),
        'month': now.month,
        'day': now.day,
        'is_weekend': 1 if now.weekday() >= 5 else 0
    }

    return round(predictor.predict(feature_dict), 2)