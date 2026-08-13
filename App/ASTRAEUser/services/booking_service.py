"""Booking form helpers — validation and category-specific fields."""
from datetime import datetime, time, timedelta

from django.utils import timezone

TIME_SLOTS = [
    ('asap', 'ASAP — earliest available'),
    ('morning', 'Morning (8 AM – 11 AM)'),
    ('afternoon', 'Afternoon (12 PM – 3 PM)'),
    ('evening', 'Evening (4 PM – 7 PM)'),
    ('night', 'Night (8 PM – 11 PM)'),
]

SLOT_START_HOURS = {
    'asap': 0,
    'morning': 8,
    'afternoon': 12,
    'evening': 16,
    'night': 20,
}


def category_needs_address(category):
    return category in {'food', 'grocery', 'shopping', 'fashion', 'beauty', 'medicine'}


def category_needs_pickup(category):
    return category == 'ride'


def category_needs_quantity(category):
    return category in {'shopping', 'grocery', 'fashion', 'beauty', 'food', 'medicine'}


def build_scheduled_at(scheduled_date, time_slot):
    """Combine date + slot into a timezone-aware datetime."""
    if not scheduled_date:
        return None
    hour = SLOT_START_HOURS.get(time_slot, 12)
    dt = datetime.combine(scheduled_date, time(hour, 0))
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def validate_booking(category, data, event=None):
    """Return dict of field errors (empty if valid)."""
    errors = {}

    scheduled_date_str = (data.get('scheduled_date') or '').strip()
    time_slot = (data.get('time_slot') or '').strip()
    pickup_location = (data.get('pickup_location') or '').strip()
    delivery_address = (data.get('delivery_address') or '').strip()
    quantity_raw = (data.get('quantity') or '1').strip()

    if not scheduled_date_str:
        errors['scheduled_date'] = 'Please select a date for your booking.'
    else:
        try:
            scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d').date()
        except ValueError:
            errors['scheduled_date'] = 'Invalid date format.'
            scheduled_date = None

        if scheduled_date and scheduled_date < timezone.localdate():
            errors['scheduled_date'] = 'Booking date cannot be in the past.'

        if scheduled_date and event:
            event_start = timezone.localtime(event.starts_at).date()
            event_end = timezone.localtime(event.ends_at).date()
            if scheduled_date < event_start:
                errors['scheduled_date'] = f'This offer starts on {event_start:%b %d, %Y}. Choose a date on or after that.'
            elif scheduled_date > event_end:
                errors['scheduled_date'] = f'This offer ends on {event_end:%b %d, %Y}. Choose an earlier date.'

    valid_slots = {code for code, _ in TIME_SLOTS}
    if not time_slot:
        errors['time_slot'] = 'Please select a preferred time slot.'
    elif time_slot not in valid_slots:
        errors['time_slot'] = 'Please choose a valid time slot.'

    if category_needs_pickup(category):
        if not pickup_location:
            errors['pickup_location'] = 'Pickup location is required for ride bookings.'
        if not delivery_address:
            errors['delivery_address'] = 'Drop location is required for ride bookings.'

    if category_needs_address(category) and not delivery_address:
        errors['delivery_address'] = 'Delivery address is required for this category.'

    if category_needs_quantity(category):
        try:
            quantity = int(quantity_raw)
            if quantity < 1 or quantity > 99:
                errors['quantity'] = 'Quantity must be between 1 and 99.'
        except ValueError:
            errors['quantity'] = 'Please enter a valid quantity.'

    return errors


def get_default_booking_date(event=None):
    """Suggest a sensible default booking date."""
    today = timezone.localdate()
    if not event:
        return today
    event_start = timezone.localtime(event.starts_at).date()
    event_end = timezone.localtime(event.ends_at).date()
    if today < event_start:
        return event_start
    if today > event_end:
        return event_end
    return today
