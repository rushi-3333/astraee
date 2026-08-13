"""Unified search orchestrator combining providers, scoring, and AIRE."""
from .providers.registry import search_all_providers
from .astrae_score_service import compute_astrae_scores, get_comparison_highlights
from .recommendation_service import rank_candidates_with_aire


def execute_smart_search(category: str, q1: str, q2: str, limit: int = 12) -> dict:
    """
    Full search pipeline:
    1. Provider search (mock + ChromaDB fallback)
    2. ASTRAE Score computation
    3. AIRE ML ranking overlay
    """
    raw_results = search_all_providers(category, q1, q2, limit=limit)

    if not raw_results:
        return {
            'all_results': [],
            'recommended': None,
            'results': [],
            'total_count': 0,
            'highlights': {},
            'errors': [],
        }

    scored = compute_astrae_scores(raw_results)
    # Merge AIRE scores where available
    try:
        aire_ranked = rank_candidates_with_aire(category, scored)
    except Exception:
        aire_ranked = scored

    # Blend ASTRAE + AIRE (60/40) for final ranking
    for item in aire_ranked:
        aire = item.get('aire_score', item.get('astrae_score', 50))
        astrae = item.get('astrae_score', 50)
        item['combined_score'] = int(round(astrae * 0.6 + aire * 0.4))
        item['astrae_score'] = item['combined_score']

    final = sorted(aire_ranked, key=lambda x: x.get('combined_score', 0), reverse=True)
    highlights = get_comparison_highlights(final)

    return {
        'all_results': final,
        'recommended': final[0] if final else None,
        'results': final[1:] if len(final) > 1 else [],
        'total_count': len(final),
        'highlights': highlights,
        'errors': [],
    }
