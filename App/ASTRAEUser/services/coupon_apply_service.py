"""Apply owned coupons at booking and mark them redeemed."""
from datetime import date
from decimal import Decimal

from django.db import transaction

from ASTRAEUser.models import UserCoupon, Notification


class CouponApplyError(Exception):
    pass


def get_applicable_coupons(user, platform):
    """Return unused, non-listed coupons owned by user for the booking platform."""
    today = date.today()
    qs = UserCoupon.objects.filter(
        user=user,
        is_used=False,
        is_for_sale=False,
        platform__iexact=platform.strip(),
        status__in=('verified', 'sold'),
    ).order_by('-face_value', '-granted_at')
    applicable = []
    for coupon in qs:
        if coupon.expiry_date and coupon.expiry_date < today:
            continue
        applicable.append(coupon)
    return applicable


def calculate_coupon_discount(coupon, final_price):
    """Compute discount amount from coupon face value, capped at 50% of order."""
    fp = Decimal(str(final_price))
    if fp <= 0:
        return Decimal('0')
    if coupon.face_value and coupon.face_value > 0:
        discount = Decimal(str(coupon.face_value))
    else:
        discount = min(fp * Decimal('0.10'), Decimal('150'))
    max_discount = fp * Decimal('0.50')
    return min(discount, max_discount, fp).quantize(Decimal('0.01'))


@transaction.atomic
def apply_coupon_at_booking(user, coupon_id, final_price, platform):
    """
    Validate and apply a user-owned coupon.
    Returns (coupon, discount_amount, coupon_code).
    """
    if not coupon_id:
        return None, Decimal('0'), ''

    try:
        coupon = UserCoupon.objects.select_for_update().get(pk=coupon_id, user=user)
    except UserCoupon.DoesNotExist:
        raise CouponApplyError('Selected coupon is not available.')

    if coupon.is_used or coupon.is_for_sale:
        raise CouponApplyError('This coupon cannot be applied.')

    if coupon.status not in ('verified', 'sold'):
        raise CouponApplyError('This coupon is not valid for use.')

    if coupon.platform.lower() != platform.strip().lower():
        raise CouponApplyError(f'This coupon is for {coupon.platform}, not {platform}.')

    if coupon.expiry_date and coupon.expiry_date < date.today():
        coupon.status = 'expired'
        coupon.save(update_fields=['status'])
        raise CouponApplyError('This coupon has expired.')

    discount = calculate_coupon_discount(coupon, final_price)
    if discount <= 0:
        raise CouponApplyError('Coupon discount could not be applied to this order.')

    return coupon, discount, coupon.coupon_code


@transaction.atomic
def redeem_coupon(coupon):
    """Mark coupon as used after successful booking."""
    coupon.is_used = True
    coupon.status = 'redeemed'
    coupon.is_for_sale = False
    coupon.save(update_fields=['is_used', 'status', 'is_for_sale'])

    Notification.objects.create(
        user=coupon.user,
        notification_type='coupon_redeemed',
        title='Coupon Used',
        message=f'You applied {coupon.coupon_code} ({coupon.platform}) on a booking.',
        link='/ASTRAEUser/usercoupons/',
    )
