"""Seed demo coupons for ASTRAE coupon marketplace."""
import random
import string
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ASTRAEUser.models import UserCoupon
from ASTRAEUser.services.coupon_pricing_service import suggest_coupon_price


PLATFORMS = [
    ('BigBasket', 'grocery'), ('Zepto', 'grocery'), ('Blinkit', 'grocery'),
    ('Swiggy', 'food'), ('Zomato', 'food'),
    ('Amazon', 'shopping'), ('Flipkart', 'shopping'),
    ('Myntra', 'fashion'), ('Ajio', 'fashion'), ('Nykaa', 'beauty'),
    ('Uber', 'ride'), ('Ola', 'ride'), ('Rapido', 'ride'),
    ('Netmeds', 'medicine'), ('PharmEasy', 'medicine'), ('Apollo Pharmacy', 'medicine'),
]

DISCOUNT_TEXTS = [
    'Flat ₹100 off', '20% off up to ₹200', '₹50 cashback', 'Free delivery',
    'Buy 1 Get 1', '₹150 off on ₹999+', '30% off first order', '₹75 instant discount',
]


def _demo_code(platform: str, idx: int) -> str:
    prefix = ''.join(c for c in platform.upper() if c.isalnum())[:4]
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'DEMO-{prefix}-{idx:04d}-{suffix}'


class Command(BaseCommand):
    help = 'Generate realistic DEMO coupons for marketplace (clearly marked as sample data)'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='Number of coupons to create')
        parser.add_argument('--list-ratio', type=float, default=0.4, help='Fraction to list for sale')
        parser.add_argument('--user', type=str, default='', help='Username to assign coupons to')

    def handle(self, *args, **options):
        count = options['count']
        list_ratio = options['list_ratio']
        username = options['user']

        if username:
            try:
                owner = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" not found.'))
                return
            owners = [owner]
        else:
            owners = list(User.objects.filter(is_active=True)[:5])
            if not owners:
                owner, _ = User.objects.get_or_create(
                    username='demo_seller',
                    defaults={'email': 'demo_seller@astrae.demo', 'is_active': True},
                )
                owners = [owner]

        created = 0
        listed = 0
        existing_codes = set(
            UserCoupon.objects.values_list('coupon_code', 'platform')
        )

        for i in range(count):
            platform, category = random.choice(PLATFORMS)
            code = _demo_code(platform, i)
            while (code, platform) in existing_codes:
                code = _demo_code(platform, random.randint(1000, 9999))
            existing_codes.add((code, platform))

            face_value = random.choice([200, 300, 500, 750, 1000, 1500])
            days = random.randint(7, 60)
            discount_text = random.choice(DISCOUNT_TEXTS)
            owner = random.choice(owners)
            is_listed = random.random() < list_ratio

            suggestion = suggest_coupon_price(face_value, face_value * 0.2, days, platform, category)
            price_pts = suggestion['suggested_price']

            coupon = UserCoupon.objects.create(
                user=owner,
                platform=platform,
                category=category,
                coupon_code=code,
                discount_text=f'[DEMO] {discount_text}',
                face_value=face_value,
                expiry_date=date.today() + timedelta(days=days),
                status='listed' if is_listed else 'verified',
                is_for_sale=is_listed,
                price_in_points=price_pts,
                is_demo=True,
                is_used=False,
            )
            if is_listed:
                from django.utils import timezone
                coupon.listed_at = timezone.now()
                coupon.save(update_fields=['listed_at'])
                listed += 1
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {created} DEMO coupons ({listed} listed for sale). '
            f'All codes prefixed with DEMO- and marked is_demo=True.'
        ))
