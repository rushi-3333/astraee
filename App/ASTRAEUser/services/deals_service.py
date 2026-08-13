"""Deals module service."""
from django.utils import timezone
from django.db.models import Q
from ASTRAEUser.models import Deal
from .astrae_score_service import compute_astrae_scores


def get_deals(filters: dict = None, sort_by: str = 'best_deal') -> list:
    filters = filters or {}
    qs = Deal.objects.filter(is_active=True)

    if filters.get('category'):
        qs = qs.filter(category=filters['category'])
    if filters.get('platform'):
        qs = qs.filter(platform_name__icontains=filters['platform'])
    if filters.get('min_discount'):
        qs = qs.filter(discount_percent__gte=float(filters['min_discount']))
    if filters.get('max_price'):
        qs = qs.filter(final_price__lte=float(filters['max_price']))

    deals = list(qs[:100])

    if sort_by == 'highest_discount':
        deals.sort(key=lambda d: d.discount_percent, reverse=True)
    elif sort_by == 'lowest_price':
        deals.sort(key=lambda d: d.final_price)
    elif sort_by == 'highest_cashback':
        deals.sort(key=lambda d: d.cashback, reverse=True)
    elif sort_by == 'ending_soon':
        deals.sort(key=lambda d: d.expires_at or timezone.now())
    else:
        deals.sort(key=lambda d: d.deal_score, reverse=True)

    return deals


def compute_deal_score(deal: Deal) -> int:
    """Transparent deal score calculation."""
    discount_pts = min(40, float(deal.discount_percent) * 0.8)
    cashback_pts = min(20, float(deal.cashback) * 0.5)
    rating_pts = float(deal.rating) * 5
    price_pts = max(0, 20 - float(deal.final_price) / 1000)
    score = int(round(discount_pts + cashback_pts + rating_pts + price_pts))
    return min(100, max(0, score))
