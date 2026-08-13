"""Run all ASTRAE seed commands in order."""
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed platforms, deals, coupons, reward rules, and demo user for demo mode'

    def add_arguments(self, parser):
        parser.add_argument('--coupons', type=int, default=80)
        parser.add_argument('--deals', type=int, default=40)

    def handle(self, *args, **options):
        call_command('seed_platforms')
        call_command('seed_deals', count=options['deals'])
        call_command('seed_coupons', count=options['coupons'])
        call_command('seed_events')
        from ASTRAEUser.services.reward_service import ensure_default_rules
        ensure_default_rules()
        self._seed_demo_user()
        self.stdout.write(self.style.SUCCESS('Demo data seed complete.'))

    def _seed_demo_user(self):
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@astrae.demo',
                'first_name': 'Demo',
                'last_name': 'User',
                'is_active': True,
            },
        )
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created demo user: demo / demo123'))
        else:
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=['is_active'])
            user.set_password('demo123')
            user.save()
            self.stdout.write('Demo user ready: demo / demo123')
        self._seed_demo_coupons(user)

    def _seed_demo_coupons(self, user):
        from datetime import date, timedelta
        from ASTRAEUser.models import UserCoupon
        platforms = ['Uber', 'Swiggy', 'Amazon', 'Netmeds']
        for i, platform in enumerate(platforms):
            code = f'DEMO-{platform.upper()[:4]}VIP{i + 1}'
            UserCoupon.objects.get_or_create(
                user=user,
                coupon_code=code,
                platform=platform,
                defaults={
                    'discount_text': f'FLAT ₹{100 + i * 50} OFF',
                    'status': 'verified',
                    'is_demo': True,
                    'face_value': 100 + i * 50,
                    'expiry_date': date.today() + timedelta(days=90),
                    'category': 'shopping',
                },
            )
