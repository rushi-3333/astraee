from .chroma_client import get_collection
from .ride_prediction_service import predict_ride_price
from .food_prediction_service import predict_food_price
from .medicine_prediction_service import predict_medicine_price
from .shopping_prediction_service import predict_shopping_price
from .recommendation_service import rank_candidates_with_aire

def execute_unified_search(category, q1, q2, limit=10):
    """
    1. Retrieval: Query ChromaDB collection based on user input.
    2. Prediction: Run AEECF CatBoost model prediction on retrieved metadata.
    3. Fallback: Default to dataset static price if ML prediction fails.
    4. Intelligent Recommendation: Pass candidate predictions through AIRE RL engine.
    5. Orchestration: Return ranked results array for view layer filtering/sorting.
    """
    try:
        return _execute_unified_search(category, q1, q2, limit=limit)
    except Exception:
        return {
            'all_results': [],
            'recommended': None,
            'results': [],
            'total_count': 0,
        }


def _execute_unified_search(category, q1, q2, limit=10):
    results = []

    if category == 'ride':
        collection = get_collection('ride_collection')
        query_str = f"{q1} {q2}".strip()
        chroma_res = collection.query(query_texts=[query_str], n_results=limit)
        metadatas = chroma_res.get('metadatas', [[]])[0]

        for meta in metadatas:
            fallback_price = float(meta.get('fare_price', meta.get('base_fare', 150.0)))
            try:
                predicted_price = predict_ride_price(meta)
            except Exception:
                predicted_price = fallback_price

            results.append({
                'platform': meta.get('platform', 'Uber'),
                'item_title': f"{meta.get('pickup_location', q1)} → {meta.get('destination', q2)}",
                'original_price': float(meta.get('fare_price', predicted_price)),
                'final_price': float(predicted_price),
                'rating': float(meta.get('driver_rating', 4.5)),
                'delivery_info': f"{meta.get('estimated_arrival_min', 5)} min ETA",
                'eta_mins': int(meta.get('estimated_arrival_min', 5)),
                'coupon_discount': float(meta.get('coupon_discount', 0)),
                'discount': float(meta.get('coupon_discount', 0)),
                'badge': 'Surge Applied' if float(meta.get('surge_multiplier', 1.0)) > 1.2 else 'Best Offer',
                'metadata': meta
            })

    elif category == 'food':
        collection = get_collection('food_collection')
        query_str = f"{q2} {q1}".strip()
        chroma_res = collection.query(query_texts=[query_str], n_results=limit)
        metadatas = chroma_res.get('metadatas', [[]])[0]

        for meta in metadatas:
            fallback_price = float(meta.get('final_price', meta.get('food_price', 250.0)))
            try:
                predicted_price = predict_food_price(meta)
            except Exception:
                predicted_price = fallback_price

            results.append({
                'platform': meta.get('platform', 'Swiggy'),
                'item_title': meta.get('food_item', 'Food Item'),
                'restaurant_name': meta.get('restaurant_name', ''),
                'original_price': float(meta.get('food_price', predicted_price)),
                'final_price': float(predicted_price),
                'rating': float(meta.get('restaurant_rating', 4.2)),
                'delivery_info': f"{meta.get('delivery_time_min', 30)} mins",
                'eta_mins': int(meta.get('delivery_time_min', 30)),
                'coupon_discount': float(meta.get('coupon_discount', 0)),
                'discount': float(meta.get('coupon_discount', 0)),
                'badge': 'Free Delivery' if meta.get('free_delivery') == 'Yes' else 'Popular',
                'metadata': meta
            })

    elif category == 'shopping':
        collection = get_collection('shopping_collection')
        query_str = f"{q2} {q1}".strip()
        chroma_res = collection.query(query_texts=[query_str], n_results=limit)
        metadatas = chroma_res.get('metadatas', [[]])[0]

        for meta in metadatas:
            fallback_price = float(meta.get('final_price', meta.get('selling_price', 900.0)))
            try:
                predicted_price = predict_shopping_price(meta)
            except Exception:
                predicted_price = fallback_price

            results.append({
                'platform': meta.get('platform', 'Amazon'),
                'item_title': meta.get('product_name', 'Product'),
                'brand': meta.get('brand', ''),
                'original_price': float(meta.get('original_price', predicted_price)),
                'final_price': float(predicted_price),
                'rating': float(meta.get('product_rating', 4.3)),
                'delivery_info': f"{meta.get('delivery_days', 3)} days",
                'eta_mins': int(meta.get('delivery_days', 3)) * 1440,
                'coupon_discount': float(meta.get('coupon_discount', 0)),
                'discount': float(meta.get('coupon_discount', 0)),
                'badge': 'Cheapest' if float(meta.get('discount_percentage', 0)) > 20 else 'Best Value',
                'metadata': meta
            })

    elif category == 'medicine':
        collection = get_collection('medicine_collection')
        query_str = f"{q2} {q1}".strip()
        chroma_res = collection.query(query_texts=[query_str], n_results=limit)
        metadatas = chroma_res.get('metadatas', [[]])[0]

        for meta in metadatas:
            fallback_price = float(meta.get('final_price', meta.get('selling_price', 100.0)))
            try:
                predicted_price = predict_medicine_price(meta)
            except Exception:
                predicted_price = fallback_price

            results.append({
                'platform': meta.get('platform', 'Netmeds'),
                'item_title': meta.get('medicine_name', 'Medicine'),
                'manufacturer': meta.get('manufacturer', ''),
                'original_price': float(meta.get('mrp', predicted_price)),
                'final_price': float(predicted_price),
                'rating': float(meta.get('platform_rating', 4.5)),
                'delivery_info': f"{meta.get('delivery_time_hours', 24)} hrs",
                'eta_mins': int(float(meta.get('delivery_time_hours', 24)) * 60),
                'coupon_discount': float(meta.get('coupon_discount', 0)),
                'discount': float(meta.get('coupon_discount', 0)),
                'badge': 'Rx Required' if meta.get('prescription_required') == 'Yes' else 'In Stock',
                'metadata': meta
            })

    # Rank candidate options using the AIRE Reinforcement Learning model
    aire_ranked_results = rank_candidates_with_aire(category, results)

    recommended = aire_ranked_results[0] if aire_ranked_results else None
    options = aire_ranked_results[1:] if len(aire_ranked_results) > 1 else []

    return {
        'all_results': aire_ranked_results,
        'recommended': recommended,
        'results': options,
        'total_count': len(aire_ranked_results)
    }