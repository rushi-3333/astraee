"""Cancel user orders with validation."""
from django.db import transaction

from ASTRAEUser.models import Order, Notification


class OrderCancelError(Exception):
    pass


CANCELLABLE = ('confirmed', 'booking_pending', 'in_progress', 'selected')


@transaction.atomic
def cancel_order(user, order_id):
    try:
        order = Order.objects.select_for_update().get(pk=order_id, user=user)
    except Order.DoesNotExist:
        raise OrderCancelError('Order not found.')

    if order.status in ('cancelled', 'completed', 'refunded'):
        raise OrderCancelError(f'This order is already {order.get_status_display().lower()}.')

    if order.status not in CANCELLABLE:
        raise OrderCancelError('This order cannot be cancelled.')

    order.status = 'cancelled'
    order.save(update_fields=['status'])

    Notification.objects.create(
        user=user,
        notification_type='order_cancelled',
        title='Booking Cancelled',
        message=f'Your booking on {order.platform} ({order.item_title}) was cancelled.',
        link='/ASTRAEUser/userorders/',
    )
    return order
