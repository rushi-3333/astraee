from datetime import datetime
from .prediction_base import AEECFPredictor

_shopping_predictor = None

def get_shopping_predictor():
    global _shopping_predictor
    if _shopping_predictor is None:
        _shopping_predictor = AEECFPredictor('Shopping_model', 'aeecf_shopping_catboost_model.pkl')
    return _shopping_predictor

def predict_shopping_price(metadata):
    now = datetime.now()
    predictor = get_shopping_predictor()

    orig_price = float(metadata.get('original_price', 1000.0))
    selling_price = float(metadata.get('selling_price', 900.0))
    coupon_discount = float(metadata.get('coupon_discount', 0.0))
    cashback = float(metadata.get('cashback', 0.0))

    feature_dict = {
        'platform': metadata.get('platform', 'Amazon'),
        'product_name': metadata.get('product_name', 'Product'),
        'brand': metadata.get('brand', 'Generic'),
        'category': metadata.get('category', 'General'),
        'subcategory': metadata.get('subcategory', 'General'),
        'original_price': orig_price,
        'selling_price': selling_price,
        'discount_percentage': float(metadata.get('discount_percentage', 10.0)),
        'cashback': cashback,
        'coupon_discount': coupon_discount,
        'effective_discount': (orig_price - selling_price) + coupon_discount + cashback,
        'delivery_days': int(metadata.get('delivery_days', 3)),
        'delivery_score': max(1, 5 - int(metadata.get('delivery_days', 3))),
        'seller_name': metadata.get('seller_name', 'Retailer'),
        'seller_rating': float(metadata.get('seller_rating', 4.5)),
        'seller_trust_score': float(metadata.get('seller_rating', 4.5)) * 20,
        'product_rating': float(metadata.get('product_rating', 4.3)),
        'review_count': int(metadata.get('review_count', 200)),
        'stock_status': metadata.get('stock_status', 'In Stock'),
        'exchange_available': metadata.get('exchange_available', 'No'),
        'exchange_flag': 1 if metadata.get('exchange_available') == 'Yes' else 0,
        'emi_available': metadata.get('emi_available', 'Yes'),
        'emi_flag': 1 if metadata.get('emi_available') == 'Yes' else 0,
        'day_of_week': metadata.get('day_of_week', now.strftime('%A')),
        'festival_indicator': int(metadata.get('festival_indicator', 0)),
        'month': now.month,
        'day': now.day,
        'is_weekend': 1 if now.weekday() >= 5 else 0
    }

    return round(predictor.predict(feature_dict), 2)