"""Check price alerts and simulate demo price drops."""
import hashlib
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from ASTRAEUser.models import PriceAlert
from ASTRAEUser.services.notification_service import create_notification


def _demo_current_price(alert: PriceAlert) -> Decimal:
    """Deterministic demo price based on alert id and date."""
    seed = f'{alert.id}:{alert.title}:{timezone.now().strftime("%Y-%m-%d")}'
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    factor = 0.7 + (h % 1000) / 1000.0 * 0.5  # 0.7 – 1.2
    base = float(alert.current_price or alert.target_price * 1.15)
    return Decimal(str(round(base * factor, 2)))


class Command(BaseCommand):
    help = 'Check price alerts and simulate demo price updates (run via cron or manually)'

    def handle(self, *args, **options):
        updated = 0
        notified = 0
        alerts = PriceAlert.objects.filter(status__in=['watching', 'offer_available'])

        for alert in alerts:
            new_price = _demo_current_price(alert)
            old_price = alert.current_price
            alert.current_price = new_price

            if new_price <= alert.target_price and alert.status != 'price_dropped':
                alert.status = 'price_dropped'
                create_notification(
                    alert.user, 'price_drop',
                    f'Price dropped: {alert.title}',
                    f'Current price ₹{new_price} is below your target of ₹{alert.target_price}.',
                    '/ASTRAEUser/useralerts/',
                )
                notified += 1
            elif new_price <= alert.target_price * Decimal('1.05'):
                alert.status = 'offer_available'

            alert.save()
            updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Checked {updated} alerts, {notified} price-drop notifications sent.'
        ))
