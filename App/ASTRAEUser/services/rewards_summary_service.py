"""Reward summary calculations from ledger."""
from django.db.models import Sum
from ASTRAEUser.models import Reward, Order
from ASTRAEUser.services.wallet_service import get_wallet_summary, sync_wallet_from_rewards
from ASTRAEUser.services.reward_service import ensure_default_rules, get_rule_points


def get_rewards_summary(user):
    ensure_default_rules()
    sync_wallet_from_rewards(user)
    wallet = get_wallet_summary(user)
    history = Reward.objects.filter(user=user).order_by('-created_at')

    lifetime_earned = history.filter(points_earned__gt=0).aggregate(Sum('points_earned'))['points_earned__sum'] or 0
    used_points = abs(history.filter(points_earned__lt=0).aggregate(Sum('points_earned'))['points_earned__sum'] or 0)
    pending_points = history.filter(status='pending').aggregate(Sum('points_earned'))['points_earned__sum'] or 0
    available_points = wallet['reward_points']

    order_savings = float(
        Order.objects.filter(user=user).aggregate(Sum('astrae_savings'))['astrae_savings__sum'] or 0
    )

    rules = {
        'order_completed': get_rule_points('order_completed', 20),
        'coupon_sold': get_rule_points('coupon_sold', 15),
        'daily_login': get_rule_points('daily_login', 5),
        'referral': get_rule_points('referral', 50),
    }

    return {
        'available_points': available_points,
        'pending_points': pending_points,
        'lifetime_points': lifetime_earned,
        'used_points': used_points,
        'total_savings': order_savings,
        'wallet': wallet,
        'history': history,
        'rules': rules,
        'total_orders': Order.objects.filter(user=user).count(),
    }
