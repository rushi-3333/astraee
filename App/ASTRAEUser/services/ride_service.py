from .chroma_client import get_collection

def search_rides(pickup, destination, vehicle_type="", limit=10):
    collection = get_collection('ride_collection')
    query_text = f"{pickup} to {destination} {vehicle_type}".strip()

    where_clause = {}
    if vehicle_type:
        where_clause["vehicle_type"] = vehicle_type

    results = collection.query(
        query_texts=[query_text],
        n_results=limit,
        where=where_clause if where_clause else None
    )

    metadatas = results.get('metadatas', [[]])[0]
    distances = results.get('distances', [[]])[0]

    normalized_results = []
    max_price = max([m.get('fare_price', 0) for m in metadatas], default=1)

    for meta, dist in zip(metadatas, distances):
        fare = float(meta.get('fare_price', 0))
        normalized_results.append({
            'platform': meta.get('platform', 'Unknown'),
            'item_title': f"{meta.get('pickup_location')} -> {meta.get('destination')}",
            'vehicle_type': meta.get('vehicle_type', ''),
            'base_price': float(meta.get('base_fare', fare)),
            'final_price': fare,
            'discount': float(meta.get('coupon_discount', 0)),
            'cashback': float(meta.get('cashback', 0)),
            'rating': float(meta.get('driver_rating', 0)),
            'eta_mins': int(meta.get('estimated_arrival_min', 0)),
            'duration_mins': int(meta.get('estimated_duration_min', 0)),
            'surge_multiplier': float(meta.get('surge_multiplier', 1.0)),
            'savings': round(max_price - fare, 2),
            'match_confidence': round(1 - dist, 4),
            'metadata': meta
        })

    # Sort results by lowest final price
    return sorted(normalized_results, key=lambda x: x['final_price'])