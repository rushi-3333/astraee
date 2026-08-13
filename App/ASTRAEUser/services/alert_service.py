"""Price & offer alert helpers."""
from decimal import Decimal
from django.utils import timezone
from ASTRAEUser.models import PriceAlert, Notification
from ASTRAEUser.services.notification_service import create_notification


def create_price_alert(user, title, target_price, platform='', category='shopping',
                       current_price=0, alert_type='price_drop', wishlist_item=None,
                       reference_id=''):
    alert = PriceAlert.objects.create(
        user=user,
        alert_type=alert_type,
        title=title,
        platform=platform,
        category=category,
        target_price=target_price,
        current_price=current_price or target_price * Decimal('1.1'),
        wishlist_item=wishlist_item,
        reference_id=reference_id,
    )
    return alert


def notify_price_drop(alert):
    savings = alert.potential_savings
    msg = (
        f'Price Drop Alert! {alert.title} is now ₹{alert.current_price}. '
        f'You can now save ₹{savings:.0f} (target ₹{alert.target_price}).'
        if savings else
        f'Price Drop Alert! {alert.title} reached your target of ₹{alert.target_price}.'
    )
    create_notification(
        alert.user, 'price_drop', f'Price Drop: {alert.title}', msg,
        '/ASTRAEUser/useralerts/',
    )


def notify_alert_triggered(alert, custom_message=''):
    type_map = {
        'coupon_expiry': ('coupon_expiring', 'Coupon Expiring Soon'),
        'deal_expiry': ('new_deal', 'Deal Expiring Soon'),
        'new_offer': ('new_deal', 'New Offer Available'),
        'event_start': ('system', 'Event Starting Soon'),
    }
    ntype, title = type_map.get(alert.alert_type, ('system', 'Alert Triggered'))
    message = custom_message or alert.alert_message
    create_notification(alert.user, ntype, title, message, '/ASTRAEUser/useralerts/')
