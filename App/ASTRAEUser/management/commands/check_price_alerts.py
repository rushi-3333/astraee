"""Check price alerts and simulate demo price drops."""
import hashlib
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from ASTRAEUser.models import PriceAlert, UserCoupon, Deal, PlatformEvent
from ASTRAEUser.services.alert_service import notify_price_drop, notify_alert_triggered


def _demo_current_price(alert: PriceAlert) -> Decimal:
    seed = f'{alert.id}:{alert.title}:{timezone.now().strftime("%Y-%m-%d")}'
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    factor = 0.7 + (h % 1000) / 1000.0 * 0.5
    base = float(alert.current_price or alert.target_price * 1.15)
    return Decimal(str(round(base * factor, 2)))


class Command(BaseCommand):
    help = 'Check price alerts and simulate demo notifications (run via cron or manually)'

    def handle(self, *args, **options):
        updated = 0
        notified = 0

        for alert in PriceAlert.objects.filter(status__in=['watching', 'offer_available']):
            if alert.alert_type == 'price_drop':
                new_price = _demo_current_price(alert)
                alert.current_price = new_price
                if new_price <= alert.target_price and alert.status != 'price_dropped':
                    alert.status = 'price_dropped'
                    notify_price_drop(alert)
                    notified += 1
                elif new_price <= alert.target_price * Decimal('1.05'):
                    alert.status = 'offer_available'
            elif alert.alert_type == 'coupon_expiry':
                pass  # handled below per coupon
            alert.save()
            updated += 1

        now = timezone.now()
        for coupon in UserCoupon.objects.filter(is_used=False, expiry_date__isnull=False):
            days = (coupon.expiry_date - timezone.localdate()).days
            if 0 <= days <= 3:
                alerts = PriceAlert.objects.filter(
                    user=coupon.user, alert_type='coupon_expiry', title__icontains=coupon.platform, status='watching',
                )
                for alert in alerts:
                    alert.status = 'triggered'
                    alert.save()
                    notify_alert_triggered(alert, f'{coupon.platform} coupon {coupon.coupon_code} — {coupon.expiry_label}.')
                    notified += 1

        for deal in Deal.objects.filter(is_active=True, expires_at__isnull=False, expires_at__lte=now + timedelta(days=2)):
            for alert in PriceAlert.objects.filter(alert_type='deal_expiry', status='watching', title__icontains=deal.title[:20]):
                alert.status = 'triggered'
                alert.save()
                notify_alert_triggered(alert, f'Deal ending soon: {deal.title}')
                notified += 1

        for event in PlatformEvent.objects.filter(is_active=True, starts_at__lte=now + timedelta(days=1), starts_at__gt=now):
            for alert in PriceAlert.objects.filter(alert_type='event_start', status='watching'):
                if alert.title.lower() in event.title.lower() or alert.platform == event.platform_name:
                    alert.status = 'triggered'
                    alert.save()
                    notify_alert_triggered(alert, f'Event starting: {event.title}')
                    notified += 1

        self.stdout.write(self.style.SUCCESS(
            f'Checked {updated} alerts, {notified} notifications sent.'
        ))
