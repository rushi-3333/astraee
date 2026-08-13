"""Events & Offers service — filter and status logic."""
from datetime import timedelta

from django.utils import timezone

from ASTRAEUser.models import PlatformEvent


def get_events(filters=None):
    filters = filters or {}
    now = timezone.now()
    qs = PlatformEvent.objects.filter(is_active=True)

    if filters.get('platform'):
        qs = qs.filter(platform_name__icontains=filters['platform'])
    if filters.get('category'):
        qs = qs.filter(category=filters['category'])

    status = filters.get('status', '')
    if status == 'upcoming':
        qs = qs.filter(starts_at__gt=now)
    elif status == 'live':
        qs = qs.filter(starts_at__lte=now, ends_at__gte=now).exclude(
            ends_at__lte=now + timedelta(days=3)
        )
    elif status == 'ending_soon':
        qs = qs.filter(
            starts_at__lte=now,
            ends_at__gte=now,
            ends_at__lte=now + timedelta(days=3),
        )

    return list(qs.order_by('starts_at'))


def get_event_counts():
    now = timezone.now()
    base = PlatformEvent.objects.filter(is_active=True)
    return {
        'all': base.count(),
        'upcoming': base.filter(starts_at__gt=now).count(),
        'live': base.filter(starts_at__lte=now, ends_at__gte=now).count(),
        'ending_soon': base.filter(
            starts_at__lte=now,
            ends_at__gte=now,
            ends_at__lte=now + timedelta(days=3),
        ).count(),
    }


PLATFORM_COLORS = {
    'Amazon': ('#FF9900', 'A'),
    'Flipkart': ('#2874F0', 'F'),
    'Myntra': ('#FF3F6C', 'M'),
    'Ajio': ('#866528', 'Aj'),
    'BigBasket': ('#84C225', 'BB'),
    'Zepto': ('#7C3AED', 'Z'),
    'Blinkit': ('#F8CB46', 'Bk'),
    'Swiggy': ('#FC8019', 'S'),
    'Zomato': ('#E23744', 'Z'),
    'Nykaa': ('#FC2779', 'N'),
    'Netmeds': ('#0066CC', 'Nm'),
    'PharmEasy': ('#10847F', 'Pe'),
    'Apollo Pharmacy': ('#007AFF', 'Ap'),
    'Uber': ('#000000', 'U'),
    'Ola': ('#347837', 'O'),
    'Rapido': ('#FFCA08', 'R'),
}
