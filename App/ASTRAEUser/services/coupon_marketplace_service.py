"""Atomic coupon marketplace purchase — server-side safety."""
from datetime import date

from django.db import transaction

from ASTRAEUser.models import UserCoupon, Reward, Wallet
from ASTRAEUser.services.reward_service import grant_reward, get_rule_points
from ASTRAEUser.services.notification_service import create_notification
from ASTRAEUser.services.wallet_service import sync_wallet_from_rewards


class CouponPurchaseError(Exception):
    pass


@transaction.atomic
def purchase_coupon_atomic(buyer, coupon_id):
    try:
        coupon = UserCoupon.objects.select_for_update().get(
            pk=coupon_id, is_for_sale=True, is_used=False,
        )
    except UserCoupon.DoesNotExist:
        raise CouponPurchaseError('This coupon is no longer available.')

    seller = coupon.user

    if seller.id == buyer.id:
        raise CouponPurchaseError('You cannot buy your own coupon.')

    if coupon.status not in ('listed', 'verified'):
        raise CouponPurchaseError('This coupon is no longer available for purchase.')

    if UserCoupon.objects.filter(
        coupon_code__iexact=coupon.coupon_code,
        platform=coupon.platform,
        status='sold',
        user=buyer,
    ).exists():
        raise CouponPurchaseError('You already own this coupon.')

    if coupon.expiry_date and coupon.expiry_date < date.today():
        coupon.status = 'expired'
        coupon.is_for_sale = False
        coupon.save(update_fields=['status', 'is_for_sale'])
        raise CouponPurchaseError('This coupon has expired.')

    sync_wallet_from_rewards(buyer)
    wallet, _ = Wallet.objects.select_for_update().get_or_create(user=buyer)
    sync_wallet_from_rewards(buyer)
    wallet.refresh_from_db()

    if wallet.reward_points < coupon.price_in_points:
        raise CouponPurchaseError(
            f'Insufficient balance! Need {coupon.price_in_points} PTS, have {wallet.reward_points} PTS.'
        )

    coupon.status = 'reserved'
    coupon.save(update_fields=['status'])

    price = coupon.price_in_points
    grant_reward(
        buyer, -price,
        f"Purchased coupon '{coupon.coupon_code}' ({coupon.platform}) from {seller.username}",
        rule_key='marketplace_purchase',
    )

    grant_reward(
        seller, price,
        f"Sold coupon '{coupon.coupon_code}' ({coupon.platform}) to {buyer.username}",
        rule_key='coupon_sold',
    )
    seller_bonus = get_rule_points('coupon_sold', 15)
    if seller_bonus:
        grant_reward(seller, seller_bonus, 'Bonus for marketplace sale', rule_key='coupon_sold')

    coupon.user = buyer
    coupon.is_for_sale = False
    coupon.status = 'sold'
    coupon.listed_at = None
    coupon.save(update_fields=['user', 'is_for_sale', 'status', 'listed_at'])

    create_notification(
        seller, 'coupon_sold', 'Coupon Sold!',
        f'Your {coupon.platform} coupon was purchased for {price} PTS.',
        '/ASTRAEUser/usercoupons/',
    )
    create_notification(
        buyer, 'coupon_purchased', 'Coupon Purchased!',
        f'You bought a {coupon.platform} coupon. Check My Coupons.',
        '/ASTRAEUser/usercoupons/',
    )

    return coupon
