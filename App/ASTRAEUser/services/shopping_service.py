from .chroma_client import get_collection

def search_shopping(product_query, category="", limit=10):
    collection = get_collection('shopping_collection')
    query_text = f"{product_query} {category}".strip()

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
            'item_title': meta.get('product_name', ''),
            'brand': meta.get('brand', ''),
            'category': meta.get('category', ''),
            'seller_name': meta.get('seller_name', ''),
            'base_price': float(meta.get('original_price', final_price)),
            'selling_price': float(meta.get('selling_price', final_price)),
            'final_price': final_price,
            'discount_pct': float(meta.get('discount_percentage', 0)),
            'cashback': float(meta.get('cashback', 0)),
            'rating': float(meta.get('product_rating', 0)),
            'seller_rating': float(meta.get('seller_rating', 0)),
            'delivery_days': int(meta.get('delivery_days', 0)),
            'stock_status': meta.get('stock_status', 'In Stock'),
            'savings': round(max_price - final_price, 2),
            'match_confidence': round(1 - dist, 4),
            'metadata': meta
        })

    return sorted(normalized_results, key=lambda x: x['final_price'])