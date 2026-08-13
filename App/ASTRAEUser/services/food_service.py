from .chroma_client import get_collection

def search_food(food_item, restaurant="", limit=10):
    collection = get_collection('food_collection')
    query_text = f"{food_item} {restaurant}".strip()

    results = collection.query(
        query_texts=[query_text],
        n_results=limit
    )

    metadatas = results.get('metadatas', [[]])[0]
    distances = results.get('distances', [[]])[0]

    normalized_results = []
    max_price = max([m.get('final_price', 0) for m in metadatas], default=1)

    for meta, dist in zip(metadatas, distances):
        final_price = float(meta.get('final_price', 0))
        normalized_results.append({
            'platform': meta.get('platform', 'Unknown'),
            'item_title': meta.get('food_item', ''),
            'restaurant_name': meta.get('restaurant_name', ''),
            'category': meta.get('category', ''),
            'base_price': float(meta.get('food_price', final_price)),
            'delivery_fee': float(meta.get('delivery_fee', 0)),
            'packaging_fee': float(meta.get('packaging_fee', 0)),
            'taxes': float(meta.get('tax_amount', 0)),
            'final_price': final_price,
            'discount': float(meta.get('coupon_discount', 0)),
            'cashback': float(meta.get('cashback', 0)),
            'rating': float(meta.get('restaurant_rating', 0)),
            'delivery_mins': int(meta.get('delivery_time_min', 0)),
            'savings': round(max_price - final_price, 2),
            'match_confidence': round(1 - dist, 4),
            'metadata': meta
        })

    return sorted(normalized_results, key=lambda x: x['final_price'])