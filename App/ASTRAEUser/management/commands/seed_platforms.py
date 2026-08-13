"""Seed categories and platforms for ASTRAE demo mode."""
from django.core.management.base import BaseCommand
from ASTRAEUser.models import Category, Platform


SEED_DATA = [
    {
        'slug': 'ride', 'name': 'Rides', 'icon': '🚗',
        'platforms': [
            ('uber', 'Uber', 85), ('ola', 'Ola', 80), ('rapido', 'Rapido', 70),
        ],
    },
    {
        'slug': 'food', 'name': 'Food', 'icon': '🍔',
        'platforms': [
            ('swiggy', 'Swiggy', 90), ('zomato', 'Zomato', 88),
        ],
    },
    {
        'slug': 'grocery', 'name': 'Grocery', 'icon': '🛒',
        'platforms': [
            ('bigbasket', 'BigBasket', 75), ('zepto', 'Zepto', 78), ('blinkit', 'Blinkit', 76),
        ],
    },
    {
        'slug': 'shopping', 'name': 'E-Commerce', 'icon': '🛍️',
        'platforms': [
            ('amazon', 'Amazon', 95), ('flipkart', 'Flipkart', 92),
        ],
    },
    {
        'slug': 'fashion', 'name': 'Fashion', 'icon': '👗',
        'platforms': [
            ('myntra', 'Myntra', 85), ('ajio', 'Ajio', 72),
        ],
    },
    {
        'slug': 'beauty', 'name': 'Beauty', 'icon': '💄',
        'platforms': [('nykaa', 'Nykaa', 80)],
    },
    {
        'slug': 'medicine', 'name': 'Medicine', 'icon': '💊',
        'platforms': [
            ('netmeds', 'Netmeds', 65), ('pharmeasy', 'PharmEasy', 68),
            ('apollo-pharmacy', 'Apollo Pharmacy', 70),
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed categories and platforms for ASTRAE demo mode'

    def handle(self, *args, **options):
        created_cats = 0
        created_plats = 0
        for item in SEED_DATA:
            cat, cat_created = Category.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'name': item['name'],
                    'icon': item['icon'],
                    'description': f'{item["name"]} comparison on ASTRAE',
                    'is_active': True,
                },
            )
            if cat_created:
                created_cats += 1
            for slug, name, pop in item['platforms']:
                _, plat_created = Platform.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'category': cat,
                        'region': 'India',
                        'status': 'active',
                        'integration_type': 'mock',
                        'api_status': 'demo',
                        'popularity_score': pop,
                    },
                )
                if plat_created:
                    created_plats += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded platforms: {created_cats} new categories, {created_plats} new platforms '
            f'({Category.objects.count()} categories, {Platform.objects.count()} platforms total).'
        ))
