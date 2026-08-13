"""Seed demo deals for ASTRAE deals hub."""
import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from ASTRAEUser.models import Deal, Platform
from ASTRAEUser.services.deals_service import compute_deal_score


DEAL_TEMPLATES = {
    'ride': [
        ('Airport ride flat ₹199', 350, 199),
        ('Weekend cab cashback ₹50', 280, 230),
        ('First ride 40% off', 200, 120),
    ],
    'food': [
        ('Biryani combo under ₹299', 450, 299),
        ('Free delivery on orders ₹199+', 350, 280),
        ('Pizza night 50% off', 600, 300),
    ],
    'grocery': [
        ('Fresh veggies under ₹1000', 1200, 899),
        ('Daily essentials bundle', 800, 649),
        ('Organic basket 25% off', 1500, 1125),
    ],
    'shopping': [
        ('iPhone 16 launch deal', 79900, 74999),
        ('Electronics sale up to 40%', 25000, 15000),
        ('Headphones under ₹2000', 3500, 1799),
    ],
    'fashion': [
        ('Sneakers flash sale', 4999, 2499),
        ('Ethnic wear 60% off', 3500, 1400),
        ('Winter collection deal', 8000, 4800),
    ],
    'beauty': [
        ('Skincare kit bundle', 2500, 1499),
        ('Makeup essentials 30% off', 1800, 1260),
    ],
    'medicine': [
        ('Cold & flu medicine pack', 450, 320),
        ('Vitamin supplements deal', 800, 560),
        ('First aid kit offer', 600, 399),
    ],
}


class Command(BaseCommand):
    help = 'Seed demo deals for ASTRAE deals page'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=40, help='Number of deals to create')

    def handle(self, *args, **options):
        count = options['count']
        platforms = list(Platform.objects.filter(status='active'))
        if not platforms:
            self.stdout.write(self.style.WARNING('No platforms found. Run seed_platforms first.'))
            return

        created = 0
        for i in range(count):
            plat = random.choice(platforms)
            cat_slug = plat.category.slug
            templates = DEAL_TEMPLATES.get(cat_slug, DEAL_TEMPLATES['shopping'])
            title, orig, final = random.choice(templates)
            title = f'{title} — {plat.name}'

            discount_pct = round((1 - final / orig) * 100, 1) if orig > 0 else 0
            deal = Deal(
                platform=plat,
                platform_name=plat.name,
                category=cat_slug,
                title=title,
                description=f'Demo deal on {plat.name}. Simulated offer for ASTRAE presentation.',
                original_price=Decimal(str(orig)),
                final_price=Decimal(str(final)),
                discount_percent=Decimal(str(discount_pct)),
                cashback=Decimal(str(random.randint(5, 50))),
                coupon_code=f'DEMO{plat.slug.upper()}{i:03d}',
                rating=Decimal(str(round(random.uniform(3.8, 4.9), 1))),
                expires_at=timezone.now() + timedelta(days=random.randint(3, 30)),
                is_active=True,
                is_demo=True,
            )
            deal.deal_score = compute_deal_score(deal)
            deal.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} demo deals ({Deal.objects.count()} total).'))
