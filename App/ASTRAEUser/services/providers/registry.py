"""
Provider registry — maps categories to platform providers.
Falls back to ChromaDB/ML pipeline when available, else uses mock providers.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from .mock_providers import (
    MockRideProvider, MockFoodProvider, MockGroceryProvider,
    MockShoppingProvider, MockMedicineProvider,
)
from .base import NormalizedResult

CATEGORY_PLATFORMS: Dict[str, List[str]] = {
    'ride': ['Uber', 'Ola', 'Rapido'],
    'food': ['Swiggy', 'Zomato'],
    'grocery': ['BigBasket', 'Zepto', 'Blinkit'],
    'shopping': ['Amazon', 'Flipkart', 'Myntra', 'Ajio'],
    'fashion': ['Myntra', 'Ajio'],
    'beauty': ['Nykaa'],
    'medicine': ['Netmeds', 'PharmEasy', 'Apollo Pharmacy'],
    'ecommerce': ['Amazon', 'Flipkart'],
}

_PROVIDER_CLASSES = {
    'ride': MockRideProvider,
    'food': MockFoodProvider,
    'grocery': MockGroceryProvider,
    'shopping': MockShoppingProvider,
    'fashion': MockShoppingProvider,
    'beauty': MockShoppingProvider,
    'medicine': MockMedicineProvider,
    'ecommerce': MockShoppingProvider,
}


def get_providers_for_category(category: str) -> list:
    platforms = CATEGORY_PLATFORMS.get(category, CATEGORY_PLATFORMS['shopping'])
    cls = _PROVIDER_CLASSES.get(category, MockShoppingProvider)
    return [cls(p) for p in platforms]


def search_all_providers(category: str, q1: str, q2: str, limit: int = 10) -> dict:
    """Search all providers in parallel; returns results and per-platform errors."""
    providers = get_providers_for_category(category)
    results = []
    errors = []

    def _fetch(provider):
        try:
            if not provider.is_available():
                return [], provider.unavailable_message()
            return [r.to_dict() for r in provider.search(q1, q2)], None
        except Exception as e:
            return [], str(e)

    with ThreadPoolExecutor(max_workers=min(len(providers), 6)) as pool:
        futures = {pool.submit(_fetch, p): p for p in providers}
        for fut in as_completed(futures):
            provider = futures[fut]
            items, err = fut.result()
            if err:
                errors.append({'platform': provider.platform_name, 'error': err})
            results.extend(items)

    # Also try ChromaDB pipeline if available
    chroma_results = _try_chroma_search(category, q1, q2, limit)
    if chroma_results:
        seen = {(r['platform'], r['item_title']) for r in results}
        for r in chroma_results:
            key = (r['platform'], r['item_title'])
            if key not in seen:
                results.append(r)
                seen.add(key)

    return {'results': results[:limit * 3], 'errors': errors}


def _try_chroma_search(category: str, q1: str, q2: str, limit: int) -> List[dict]:
    try:
        from ..comparison_service import execute_unified_search
        output = execute_unified_search(category, q1, q2, limit=limit)
        return output.get('all_results', [])
    except Exception:
        return []
