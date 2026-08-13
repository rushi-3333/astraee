from .chroma_client import get_collection

def search_medicine(medicine_query, limit=10):
    collection = get_collection('medicine_collection')

    results = collection.query(
        query_texts=[medicine_query],
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
            'item_title': meta.get('medicine_name', ''),
            'composition': meta.get('composition', ''),
            'manufacturer': meta.get('manufacturer', ''),
            'pack_size': meta.get('pack_size', ''),
            'base_price': float(meta.get('mrp', final_price)),
            'selling_price': float(meta.get('selling_price', final_price)),
            'final_price': final_price,
            'discount_pct': float(meta.get('discount_percentage', 0)),
            'cashback': float(meta.get('cashback', 0)),
            'rating': float(meta.get('platform_rating', 0)),
            'delivery_hours': float(meta.get('delivery_time_hours', 0)),
            'prescription_required': meta.get('prescription_required', 'No'),
            'stock_status': meta.get('stock_status', 'In Stock'),
            'savings': round(max_price - final_price, 2),
            'match_confidence': round(1 - dist, 4),
            'metadata': meta
        })

    return sorted(normalized_results, key=lambda x: x['final_price'])