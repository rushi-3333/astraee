"""Run all ASTRAE seed commands in order."""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed platforms, deals, coupons, and reward rules for demo mode'

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
        self.stdout.write(self.style.SUCCESS('Demo data seed complete.'))
