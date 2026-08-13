"""Configurable reward rules — server-side point calculations."""
from django.db import transaction
from ASTRAEUser.models import Reward, RewardRule, Notification


DEFAULT_RULES = [
    ('order_completed', 'Order Completed', 20, 'Points for completing an order'),
    ('coupon_sold', 'Coupon Sold', 15, 'Bonus for selling a coupon'),
    ('daily_login', 'Daily Login', 5, 'Daily login bonus'),
    ('referral', 'Referral', 50, 'Refer a friend bonus'),
    ('marketplace_purchase', 'Marketplace Purchase', 0, 'Coupon purchase (deduction)'),
]


def ensure_default_rules():
    for key, name, points, desc in DEFAULT_RULES:
        RewardRule.objects.get_or_create(
            key=key,
            defaults={'name': name, 'points': points, 'description': desc, 'is_active': True},
        )


def get_rule_points(key: str, fallback: int = 20) -> int:
    ensure_default_rules()
    try:
        rule = RewardRule.objects.get(key=key, is_active=True)
        return rule.points
    except RewardRule.DoesNotExist:
        return fallback


class InsufficientPointsError(Exception):
    pass


@transaction.atomic
def grant_reward(user, points: int, description: str, order=None, rule_key: str = '', status: str = 'earned'):
    if points < 0:
        from ASTRAEUser.models import Wallet
        sync_wallet_from_rewards(user)
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=user)
        sync_wallet_from_rewards(user)
        wallet.refresh_from_db()
        if wallet.reward_points + points < 0:
            raise InsufficientPointsError('Insufficient reward points for this transaction.')

    reward = Reward.objects.create(
        user=user,
        order=order,
        points_earned=points,
        description=description,
        rule_key=rule_key,
        status=status,
    )
    if points > 0:
        Notification.objects.create(
            user=user,
            notification_type='reward_earned',
            title=f'+{points} ASTRAE Points',
            message=description,
            link='/ASTRAEUser/userrewards/',
        )
    from .wallet_service import sync_wallet_from_rewards
    sync_wallet_from_rewards(user)
    return reward
