"""Savings dashboard — computed from real order, reward, and coupon data."""
from decimal import Decimal
from django.db.models import Sum, Count
from django.utils import timezone
from ASTRAEUser.models import Order, Reward, UserCoupon


def compute_savings_dashboard(user):
    orders = Order.objects.filter(user=user)
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_spent = float(orders.aggregate(Sum('final_price'))['final_price__sum'] or 0)
    total_saved = float(orders.aggregate(Sum('astrae_savings'))['astrae_savings__sum'] or 0)
    comparison_savings = total_saved
    coupon_savings = float(orders.aggregate(Sum('discount'))['discount__sum'] or 0)
    cashback_savings = float(orders.aggregate(Sum('cashback'))['cashback__sum'] or 0)

    month_orders = orders.filter(created_at__gte=month_start)
    month_saved = float(month_orders.aggregate(Sum('astrae_savings'))['astrae_savings__sum'] or 0)
    month_spent = float(month_orders.aggregate(Sum('final_price'))['final_price__sum'] or 0)

    rewards = Reward.objects.filter(user=user)
    total_points = rewards.aggregate(Sum('points_earned'))['points_earned__sum'] or 0
    reward_savings = max(0, int(total_points))  # 1 point ≈ ₹1 demo value for display

    marketplace_earnings = rewards.filter(
        description__icontains='Sold coupon'
    ).aggregate(Sum('points_earned'))['points_earned__sum'] or 0

    marketplace_savings = float(
        UserCoupon.objects.filter(user=user, is_for_sale=False, is_used=False).aggregate(
            total=Sum('face_value')
        )['total'] or 0
    )

    category_spending = list(
        orders.values('category').annotate(total=Sum('final_price'), count=Count('id')).order_by('-total')
    )
    platform_usage = list(
        orders.values('platform').annotate(count=Count('id')).order_by('-count')[:8]
    )

    monthly = {}
    for o in orders:
        month_key = o.created_at.strftime('%Y-%m')
        if month_key not in monthly:
            monthly[month_key] = {'spent': 0, 'saved': 0}
        monthly[month_key]['spent'] += float(o.final_price)
        monthly[month_key]['saved'] += float(o.astrae_savings)

    has_real_data = orders.exists()
    headline_saved = total_saved if has_real_data else Decimal('0')

    return {
        'total_spent': total_spent,
        'total_saved': float(headline_saved),
        'month_saved': month_saved,
        'month_spent': month_spent,
        'comparison_savings': comparison_savings,
        'coupon_savings': coupon_savings,
        'cashback_savings': cashback_savings,
        'reward_savings': reward_savings,
        'marketplace_earnings': marketplace_earnings,
        'marketplace_savings': marketplace_savings,
        'total_points': total_points,
        'has_real_data': has_real_data,
        'category_spending': category_spending,
        'platform_usage': platform_usage,
        'monthly': monthly,
    }
