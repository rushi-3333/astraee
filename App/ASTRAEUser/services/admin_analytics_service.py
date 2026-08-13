"""Admin dashboard analytics."""
import json
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from ASTRAEUser.models import (
    Order, UserCoupon, Reward, SearchHistory, Platform, PriceAlert, Wallet,
)


def get_admin_dashboard_metrics():
    users = User.objects.filter(is_staff=False, is_superuser=False)
    active_users = users.filter(is_active=True).count()
    total_users = users.count()
    total_orders = Order.objects.count()
    total_coupons = UserCoupon.objects.count()
    marketplace_listed = UserCoupon.objects.filter(is_for_sale=True, is_used=False, status='listed').count()
    total_searches = SearchHistory.objects.count()
    rewards_distributed = Reward.objects.filter(points_earned__gt=0).aggregate(
        Sum('points_earned')
    )['points_earned__sum'] or 0
    total_savings = float(Order.objects.aggregate(Sum('astrae_savings'))['astrae_savings__sum'] or 0)
    coupon_sales = Reward.objects.filter(description__icontains='Sold coupon').count()
    marketplace_activity = UserCoupon.objects.filter(status='sold').count()

    category_counts = Order.objects.values('category').annotate(total=Count('id'))
    category_data = {c['category']: c['total'] for c in category_counts}
    cat_labels = ['Rides', 'Food', 'Grocery', 'Shopping', 'Fashion', 'Beauty', 'Medicine']
    cat_values = [
        category_data.get('ride', 0),
        category_data.get('food', 0),
        category_data.get('grocery', 0),
        category_data.get('shopping', 0),
        category_data.get('fashion', 0),
        category_data.get('beauty', 0),
        category_data.get('medicine', 0),
    ]

    platform_counts = Order.objects.values('platform').annotate(total=Count('id')).order_by('-total')[:8]
    platform_labels = [p['platform'] for p in platform_counts]
    platform_values = [p['total'] for p in platform_counts]

    # Orders over last 7 days
    week_ago = timezone.now() - timedelta(days=7)
    daily_orders = {}
    for o in Order.objects.filter(created_at__gte=week_ago):
        day = o.created_at.strftime('%a')
        daily_orders[day] = daily_orders.get(day, 0) + 1

    platform_health = []
    for p in Platform.objects.select_related('category').order_by('category__name', 'name'):
        health = 'Active' if p.status == 'active' and p.api_status != 'demo' else (
            'Demo' if p.api_status == 'demo' or p.integration_type == 'mock' else 'Unavailable'
        )
        if p.status == 'maintenance':
            health = 'Unavailable'
        platform_health.append({
            'name': p.name,
            'category': p.category.name if p.category else '',
            'integration': p.integration_type,
            'health': health,
        })

    return {
        'total_users_count': total_users,
        'active_users_count': active_users,
        'total_orders_count': total_orders,
        'total_coupons_count': total_coupons,
        'marketplace_listed_count': marketplace_listed,
        'total_searches_count': total_searches,
        'rewards_distributed': rewards_distributed,
        'total_user_savings': total_savings,
        'coupon_sales_count': coupon_sales,
        'marketplace_activity_count': marketplace_activity,
        'cat_labels_json': json.dumps(cat_labels),
        'cat_values_json': json.dumps(cat_values),
        'platform_labels_json': json.dumps(platform_labels),
        'platform_values_json': json.dumps(platform_values),
        'daily_orders_json': json.dumps(daily_orders),
        'platform_health': platform_health,
    }
