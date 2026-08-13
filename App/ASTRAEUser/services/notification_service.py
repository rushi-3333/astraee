"""Notification helpers."""
from ASTRAEUser.models import Notification


def create_notification(user, notification_type: str, title: str, message: str, link: str = ''):
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )


def get_unread_count(user) -> int:
    if not user.is_authenticated:
        return 0
    return Notification.objects.filter(user=user, is_read=False).count()


def mark_all_read(user):
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)
