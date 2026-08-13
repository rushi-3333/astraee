"""Server-side price resolution for bookings — never trust client-submitted prices."""
from decimal import Decimal

from .unified_search_service import execute_smart_search


def resolve_booking_prices(platform, category, item_title, q1='', q2='', event=None):
    """
    Resolve authoritative prices from the search pipeline.
    Returns dict with final_price, original_price, cashback, discount or None if unmatched.
    """
    if event:
        return {
            'final_price': Decimal('0'),
            'original_price': Decimal('0'),
            'cashback': Decimal('0'),
            'discount': Decimal('0'),
        }

    search_q1 = (q1 or '').strip() or 'Hyderabad'
    search_q2 = (q2 or '').strip() or (item_title or '').strip()
    if not search_q2:
        return None

    output = execute_smart_search(category, search_q1, search_q2, limit=30)
    platform_l = (platform or '').lower().strip()
    title_l = (item_title or '').lower().strip()

    best_match = None
    for item in output.get('all_results', []):
        if item.get('platform', '').lower().strip() != platform_l:
            continue
        item_title_val = (item.get('item_title') or '').lower()
        if title_l in item_title_val or item_title_val in title_l:
            best_match = item
            break

    if not best_match:
        for item in output.get('all_results', []):
            if item.get('platform', '').lower().strip() == platform_l:
                best_match = item
                break

    if not best_match:
        return None

    final = Decimal(str(best_match.get('final_price', 0)))
    original = Decimal(str(best_match.get('original_price', final)))
    if final <= 0 or final > Decimal('1000000'):
        return None

    return {
        'final_price': final,
        'original_price': max(original, final),
        'cashback': Decimal(str(best_match.get('cashback', 0))),
        'discount': Decimal(str(best_match.get('discount', 0))),
    }
