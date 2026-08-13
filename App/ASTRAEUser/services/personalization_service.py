"""Personalized recommendations based on user activity."""
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from ASTRAEUser.models import (
    Order, SearchHistory, WishlistItem, Deal, UserCoupon, PlatformEvent, PriceAlert,
)

MIN_PERSONALIZATION_SIGNALS = 3


def get_personalized_recommendations(user) -> dict:
    if not user.is_authenticated:
        return _anonymous_recommendations()

    orders = Order.objects.filter(user=user)
    search_count = SearchHistory.objects.filter(user=user).count()
    order_count = orders.count()
    signal_count = order_count + search_count

    category_counts = orders.values('category').annotate(c=Count('id')).order_by('-c')
    top_category = category_counts[0]['category'] if category_counts else None

    if not top_category:
        recent_search = SearchHistory.objects.filter(user=user).order_by('-created_at').first()
        top_category = recent_search.category if recent_search else 'shopping'

    platform_counts = orders.values('platform').annotate(c=Count('id')).order_by('-c')
    top_platform = platform_counts[0]['platform'] if platform_counts else 'Amazon'

    is_personalized = signal_count >= MIN_PERSONALIZATION_SIGNALS
    section_title = 'Picked for you' if is_personalized else 'Trending on ASTRAE'

    if is_personalized:
        deals = list(Deal.objects.filter(category=top_category, is_active=True).order_by('-deal_score')[:6])
        if not deals:
            deals = list(Deal.objects.filter(is_active=True).order_by('-deal_score')[:6])
    else:
        deals = list(Deal.objects.filter(is_active=True).order_by('-deal_score')[:6])

    now = timezone.now()
    expiring_deals = list(
        Deal.objects.filter(is_active=True, expires_at__lte=now + timedelta(days=3), expires_at__gte=now)
        .order_by('expires_at')[:4]
    )
    upcoming_events = list(
        PlatformEvent.objects.filter(is_active=True, starts_at__gt=now).order_by('starts_at')[:4]
    )
    live_events = list(
        PlatformEvent.objects.filter(is_active=True, starts_at__lte=now, ends_at__gte=now).order_by('-starts_at')[:4]
    )

    price_drops = PriceAlert.objects.filter(user=user, status='price_dropped')[:3]
    wishlist_count = WishlistItem.objects.filter(user=user).count()

    messages = []
    if is_personalized and category_counts:
        cat_name = top_category.replace('_', ' ').title()
        messages.append({
            'type': 'personal',
            'text': f"Because you frequently use {cat_name}, here are top picks for you.",
        })
    elif not is_personalized:
        messages.append({
            'type': 'trending',
            'text': 'Popular deals across ASTRAE — sign in and search more for personalized picks.',
        })

    total_spent = float(orders.aggregate(Sum('final_price'))['final_price__sum'] or 0)
    total_saved = float(orders.aggregate(Sum('astrae_savings'))['astrae_savings__sum'] or 0)

    recent_searches = SearchHistory.objects.filter(user=user).order_by('-created_at')[:5]

    return {
        'section_title': section_title,
        'is_personalized': is_personalized,
        'top_category': top_category,
        'top_platform': top_platform,
        'deals': deals,
        'expiring_deals': expiring_deals,
        'upcoming_events': upcoming_events,
        'live_events': live_events,
        'price_drops': price_drops,
        'wishlist_count': wishlist_count,
        'messages': messages,
        'recent_searches': recent_searches,
        'order_count': order_count,
        'total_spent': total_spent,
        'total_saved': total_saved,
    }


def _anonymous_recommendations():
    deals = list(Deal.objects.filter(is_active=True).order_by('-deal_score')[:6])
    now = timezone.now()
    return {
        'section_title': 'Trending on ASTRAE',
        'is_personalized': False,
        'top_category': 'shopping',
        'top_platform': 'Amazon',
        'deals': deals,
        'expiring_deals': list(
            Deal.objects.filter(is_active=True, expires_at__lte=now + timedelta(days=3), expires_at__gte=now)[:4]
        ),
        'upcoming_events': list(PlatformEvent.objects.filter(is_active=True, starts_at__gt=now)[:4]),
        'live_events': list(
            PlatformEvent.objects.filter(is_active=True, starts_at__lte=now, ends_at__gte=now)[:4]
        ),
        'price_drops': [],
        'wishlist_count': 0,
        'messages': [{'type': 'welcome', 'text': 'Sign in for personalized picks based on your activity.'}],
        'recent_searches': [],
        'order_count': 0,
        'total_spent': 0,
        'total_saved': 0,
    }
