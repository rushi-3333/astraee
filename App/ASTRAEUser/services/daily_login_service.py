"""Grant daily login bonus once per calendar day."""
from django.utils import timezone

from ASTRAEUser.models import Reward, Notification
from .reward_service import grant_reward, get_rule_points


def grant_daily_login_bonus(user):
    """
    Award daily login points if not already granted today.
    Returns (points, True) if granted, (0, False) if already claimed.
    """
    today = timezone.localdate()
    already = Reward.objects.filter(
        user=user,
        rule_key='daily_login',
        created_at__date=today,
    ).exists()
    if already:
        return 0, False

    points = get_rule_points('daily_login', 5)
    if points <= 0:
        return 0, False

    grant_reward(
        user,
        points,
        'Daily login bonus',
        rule_key='daily_login',
    )
    Notification.objects.create(
        user=user,
        notification_type='reward_earned',
        title=f'+{points} Daily Login Bonus',
        message='Thanks for checking in today!',
        link='/ASTRAEUser/userrewards/',
    )
    return points, True
