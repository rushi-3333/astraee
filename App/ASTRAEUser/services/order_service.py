import os
import random
import pandas as pd
from django.conf import settings
from ASTRAEUser.models import Order, Reward, UserCoupon

DATASET_PATH = os.path.join(settings.BASE_DIR, 'Model', 'user_interaction_rl_dataset.csv')

def process_booking(user, platform, category, item_title, final_price):
    # 1. Save Order to Database
    order = Order.objects.create(
        user=user,
        platform=platform,
        category=category,
        item_title=item_title,
        final_price=final_price
    )

    # 2. Grant Random Reward Points between 1 and 10,000
    earned_points = random.randint(1, 10000)
    
    reward = Reward.objects.create(
        user=user,
        order=order,
        points_earned=earned_points,
        description=f"Reward for booking {item_title} on {platform}"
    )

    # 3. Pick Coupon from Dataset
    coupon_code, discount_text = _extract_coupon_from_dataset(platform)

    # 4. Save Issued Coupon
    granted_coupon = UserCoupon.objects.create(
        user=user,
        platform=platform,
        coupon_code=coupon_code,
        discount_text=discount_text
    )

    return order, reward, granted_coupon

def _extract_coupon_from_dataset(platform):
    if os.path.exists(DATASET_PATH):
        try:
            df = pd.read_csv(DATASET_PATH)
            if 'platform' in df.columns and 'applied_coupon' in df.columns:
                platform_matches = df[df['platform'].str.lower() == platform.lower()]
                if not platform_matches.empty and 'applied_coupon' in platform_matches.columns:
                    sample_code = str(platform_matches['applied_coupon'].sample(1).iloc[0])
                    if sample_code and sample_code != 'nan':
                        return sample_code, f"FLAT ₹{random.randint(30, 150)} OFF"
        except Exception:
            pass

    rand_id = random.randint(100, 999)
    return f"{platform.upper()[:4]}SAVE{rand_id}", f"FLAT ₹{random.randint(30, 100)} OFF"