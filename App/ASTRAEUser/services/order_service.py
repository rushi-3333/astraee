import os
import random
import pandas as pd
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from ASTRAEUser.models import Order, UserCoupon, Notification
from .reward_service import grant_reward, get_rule_points

DATASET_PATH = os.path.join(settings.BASE_DIR, 'Model', 'user_interaction_rl_dataset.csv')


@transaction.atomic
def process_booking(user, platform, category, item_title, final_price,
                    original_price=None, discount=0, coupon_applied='', cashback=0,
                    event=None, scheduled_at=None, time_slot='', quantity=1,
                    pickup_location='', delivery_address='', booking_notes=''):
    fp = Decimal(str(final_price))
    op = Decimal(str(original_price)) if original_price else fp
    savings = max(Decimal('0'), op - fp) + Decimal(str(cashback))

    order = Order.objects.create(
        user=user,
        platform=platform,
        category=category,
        item_title=item_title,
        final_price=fp,
        original_price=op,
        discount=Decimal(str(discount)),
        coupon_applied=coupon_applied,
        cashback=Decimal(str(cashback)),
        astrae_savings=savings,
        status='confirmed',
        event=event,
        scheduled_at=scheduled_at,
        time_slot=time_slot,
        quantity=max(1, int(quantity or 1)),
        pickup_location=pickup_location or '',
        delivery_address=delivery_address or '',
        booking_notes=booking_notes or '',
    )

    earned_points = get_rule_points('order_completed', fallback=20)
    reward = grant_reward(
        user=user,
        points=earned_points,
        description=f"Reward for booking {item_title} on {platform}",
        order=order,
        rule_key='order_completed',
    )

    coupon_code, discount_text = _extract_coupon_from_dataset(platform)
    granted_coupon = UserCoupon.objects.create(
        user=user,
        platform=platform,
        coupon_code=coupon_code,
        discount_text=discount_text,
        status='verified',
        is_demo=True,
        category=category,
    )

    schedule_text = ''
    if scheduled_at:
        schedule_text = f' Scheduled for {scheduled_at:%b %d, %Y}'
    if time_slot:
        schedule_text += f' ({time_slot.replace("_", " ")})'

    Notification.objects.create(
        user=user,
        notification_type='order_completed',
        title='Booking Confirmed',
        message=f'Your booking on {platform} is confirmed.{schedule_text} You earned +{earned_points} points!',
        link='/ASTRAEUser/userorders/',
    )

    return order, reward, granted_coupon


def _extract_coupon_from_dataset(platform):
    if os.path.exists(DATASET_PATH):
        try:
            df = pd.read_csv(DATASET_PATH)
            if 'platform' in df.columns and 'applied_coupon' in df.columns:
                platform_matches = df[df['platform'].str.lower() == platform.lower()]
                if not platform_matches.empty:
                    sample_code = str(platform_matches['applied_coupon'].sample(1).iloc[0])
                    if sample_code and sample_code != 'nan':
                        return f"DEMO-{sample_code}", f"FLAT ₹{random.randint(30, 150)} OFF"
        except Exception:
            pass

    rand_id = random.randint(100, 999)
    prefix = platform.upper().replace(' ', '')[:4]
    return f"DEMO-{prefix}SAVE{rand_id}", f"FLAT ₹{random.randint(30, 100)} OFF"
