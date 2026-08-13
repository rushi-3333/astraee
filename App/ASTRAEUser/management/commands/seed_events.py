"""Seed demo events and offers for ASTRAE Events page."""
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from ASTRAEUser.models import PlatformEvent, Platform


EVENT_TYPES = ['festival', 'flash_sale', 'live_offer', 'platform_offer', 'upcoming']

EVENT_TEMPLATES = [
    ('Amazon', 'shopping', 'Great Indian Festival', 'Up to 70% off on electronics & fashion', 'Annual mega sale with bank offers and no-cost EMI.'),
    ('Amazon', 'shopping', 'Prime Day Preview', 'Exclusive early deals for members', 'Prime members get 24-hour early access to top deals.'),
    ('Flipkart', 'shopping', 'Big Billion Days', 'Lowest prices of the year', 'Smartphones, appliances, and fashion at blockbuster prices.'),
    ('Flipkart', 'shopping', 'Electronics Carnival', 'Extra ₹3000 off on laptops', 'Exchange bonuses and instant discounts on gadgets.'),
    ('Myntra', 'fashion', 'End of Reason Sale', '50–80% off on top brands', 'Fashion, footwear, and accessories mega clearance.'),
    ('Myntra', 'fashion', 'Festive Wardrobe Sale', 'Buy 2 Get 1 Free', 'Curated ethnic and party wear collections.'),
    ('Ajio', 'fashion', 'All Stars Sale', 'Flat 60% off + extra coupon', 'Street style and premium fashion brands.'),
    ('Ajio', 'fashion', 'Sneaker Fest', 'Starting ₹999 on sneakers', 'Limited edition drops from global brands.'),
    ('BigBasket', 'grocery', 'BB Daily Bonanza', 'Flat ₹150 off on ₹1500+', 'Fresh produce, staples, and household essentials.'),
    ('BigBasket', 'grocery', 'Organic Week', '25% off on organic range', 'Farm-fresh organic fruits, vegetables, and grains.'),
    ('Zepto', 'grocery', '10-Minute Grocery Fest', 'Free delivery on orders ₹99+', 'Quick commerce flash deals every hour.'),
    ('Blinkit', 'grocery', 'Midnight Snack Sale', 'Up to 40% off snacks', 'Late-night munchies and beverages at special prices.'),
    ('Swiggy', 'food', 'Food Festival Week', 'Flat 60% off up to ₹120', 'Top restaurants and cloud kitchens participating.'),
    ('Swiggy', 'food', 'Weekend Biryani Bash', 'Biryani from ₹149', 'Hyderabadi, Lucknowi, and Kolkata specials.'),
    ('Zomato', 'food', 'Gold Member Exclusive', 'Extra 20% off + free delivery', 'Gold members save more on dining and delivery.'),
    ('Zomato', 'food', 'Pizza Party Weekend', 'Buy 1 Get 1 on pizzas', 'Domino\'s, Pizza Hut, and local favorites.'),
    ('Nykaa', 'beauty', 'Pink Friday Sale', 'Up to 50% off beauty', 'Skincare, makeup, and fragrance from top brands.'),
    ('Nykaa', 'beauty', 'Summer Glow Fest', 'Free gifts on ₹999+', 'Sunscreen, serums, and summer essentials.'),
    ('Netmeds', 'medicine', 'Health Days Sale', 'Up to 25% off medicines', 'Prescription and OTC medicines at discounted prices.'),
    ('PharmEasy', 'medicine', 'Flash Medicine Sale', 'Extra 20% off + free delivery', 'Quick medicine delivery flash offer.'),
    ('Apollo Pharmacy', 'medicine', 'Wellness Weekend', 'Buy 2 Get 1 on vitamins', 'Immunity boosters and daily wellness products.'),
    ('Uber', 'ride', 'City Commute Week', 'Flat ₹50 off on 5 rides', 'Save on daily office and metro-connect rides.'),
    ('Ola', 'ride', 'Weekend Outstation Offer', '15% off on outstation trips', 'Plan your weekend getaway with discounted cab fares.'),
]


class Command(BaseCommand):
    help = 'Seed demo events and offers for the Events & Offers page'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=24, help='Number of events to create')

    def handle(self, *args, **options):
        count = options['count']
        now = timezone.now()
        created = 0

        platforms = {p.name: p for p in Platform.objects.all()}

        for i in range(count):
            platform_name, category, title, benefit, desc = random.choice(EVENT_TEMPLATES)
            title = f'{title} (Demo {i + 1})'

            # Spread events across upcoming, live, and ending soon
            roll = i % 3
            if roll == 0:
                starts = now + timedelta(days=random.randint(2, 14))
                ends = starts + timedelta(days=random.randint(5, 10))
            elif roll == 1:
                starts = now - timedelta(days=random.randint(1, 5))
                ends = now + timedelta(days=random.randint(7, 21))
            else:
                starts = now - timedelta(days=random.randint(3, 10))
                ends = now + timedelta(days=random.randint(1, 3))

            plat = platforms.get(platform_name)
            PlatformEvent.objects.create(
                platform=plat,
                platform_name=platform_name,
                category=category,
                title=title,
                description=f'[DEMO] {desc} Simulated offer for ASTRAE presentation — not a live external promotion.',
                main_benefit=benefit,
                event_type=EVENT_TYPES[i % len(EVENT_TYPES)],
                starts_at=starts,
                ends_at=ends,
                is_active=True,
                is_demo=True,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {created} demo events ({PlatformEvent.objects.count()} total). '
            f'All marked is_demo=True.'
        ))
