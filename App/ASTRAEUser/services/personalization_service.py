"""Personalized recommendations based on user behavior."""
from django.db.models import Count
from ASTRAEUser.models import Order, SearchHistory, WishlistItem, Deal, UserCoupon


def get_personalized_recommendations(user) -> dict:
    if not user.is_authenticated:
        return _anonymous_recommendations()

    orders = Order.objects.filter(user=user)
    category_counts = orders.values('category').annotate(c=Count('id')).order_by('-c')
    top_category = category_counts[0]['category'] if category_counts else 'shopping'

    platform_counts = orders.values('platform').annotate(c=Count('id')).order_by('-c')
    top_platform = platform_counts[0]['platform'] if platform_counts else 'Amazon'

    deals = list(Deal.objects.filter(category=top_category, is_active=True).order_by('-deal_score')[:6])
    if not deals:
        deals = list(Deal.objects.filter(is_active=True).order_by('-deal_score')[:6])

    total_spent = sum(float(o.final_price) for o in orders)
    potential_savings = round(total_spent * 0.12, 2)

    messages = []
    if category_counts:
        cat_name = top_category.replace('_', ' ').title()
        messages.append({
            'type': 'category',
            'text': f"Because you frequently shop for {cat_name}, here are today's best {cat_name} deals.",
        })
    if potential_savings > 0:
        messages.append({
            'type': 'savings',
            'text': f"Based on your purchase history, you could save ₹{potential_savings:.0f} with available coupons.",
        })

    recent_searches = SearchHistory.objects.filter(user=user).order_by('-created_at')[:5]

    return {
        'top_category': top_category,
        'top_platform': top_platform,
        'deals': deals,
        'messages': messages,
        'recent_searches': recent_searches,
        'order_count': orders.count(),
    }


def _anonymous_recommendations():
    deals = list(Deal.objects.filter(is_active=True).order_by('-deal_score')[:6])
    return {
        'top_category': 'shopping',
        'top_platform': 'Amazon',
        'deals': deals,
        'messages': [{'type': 'welcome', 'text': 'Sign in for personalized recommendations based on your shopping habits.'}],
        'recent_searches': [],
        'order_count': 0,
    }
