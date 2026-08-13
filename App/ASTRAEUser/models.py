from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


# ─── Existing core models (preserved) ───────────────────────────────────────

class Order(models.Model):
    STATUS_CHOICES = [
        ('searching', 'Searching'),
        ('selected', 'Selected'),
        ('booking_pending', 'Booking Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    platform = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    item_title = models.CharField(max_length=255)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_applied = models.CharField(max_length=100, blank=True, default='')
    cashback = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    astrae_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    event = models.ForeignKey(
        'PlatformEvent', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders',
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    time_slot = models.CharField(max_length=50, blank=True, default='')
    quantity = models.PositiveIntegerField(default=1)
    pickup_location = models.CharField(max_length=255, blank=True, default='')
    delivery_address = models.CharField(max_length=255, blank=True, default='')
    booking_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['platform']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.platform} ({self.item_title})"

    @property
    def time_slot_label(self):
        from ASTRAEUser.services.booking_service import TIME_SLOTS
        return dict(TIME_SLOTS).get(self.time_slot, self.time_slot.replace('_', ' ').title())


class Reward(models.Model):
    STATUS_CHOICES = [
        ('earned', 'Earned'),
        ('pending', 'Pending'),
        ('redeemed', 'Redeemed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
    points_earned = models.IntegerField(default=50)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='earned')
    rule_key = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['user', '-created_at'])]

    def __str__(self):
        return f"{self.user.username} - {self.points_earned} Points"


class UserCoupon(models.Model):
    STATUS_CHOICES = [
        ('pending_verification', 'Pending Verification'),
        ('verified', 'Verified'),
        ('listed', 'Listed'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupons')
    platform = models.CharField(max_length=100)
    coupon_code = models.CharField(max_length=50)
    discount_text = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)
    is_for_sale = models.BooleanField(default=False)
    price_in_points = models.IntegerField(default=50)
    listed_at = models.DateTimeField(null=True, blank=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    # Extended marketplace fields
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='verified')
    face_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expiry_date = models.DateField(null=True, blank=True)
    is_demo = models.BooleanField(default=True, help_text='Demo/sample coupon for development')
    category = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['is_for_sale', 'status']),
            models.Index(fields=['platform']),
            models.Index(fields=['expiry_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['coupon_code', 'platform'],
                name='unique_coupon_per_platform',
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.coupon_code} ({self.platform})"

    @property
    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.localdate()).days

    @property
    def expiry_label(self):
        days = self.days_until_expiry
        if days is None:
            return 'No expiry set'
        if days < 0:
            return 'Expired'
        if days == 0:
            return 'Expires today'
        if days == 1:
            return 'Expires in 1 day'
        return f'Expires in {days} days'

    @property
    def is_verified_coupon(self):
        return self.status in ('verified', 'listed', 'sold') and not self.is_used


# ─── Platform & Category management ─────────────────────────────────────────

class Category(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='📦')
    description = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Platform(models.Model):
    INTEGRATION_CHOICES = [
        ('mock', 'Mock'),
        ('api', 'API'),
        ('affiliate', 'Affiliate'),
        ('manual', 'Manual'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='platforms')
    region = models.CharField(max_length=100, default='India')
    logo_url = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_CHOICES, default='mock')
    api_status = models.CharField(max_length=50, default='demo')
    popularity_score = models.IntegerField(default=50)

    class Meta:
        indexes = [models.Index(fields=['category', 'status'])]

    def __str__(self):
        return self.name


# ─── Deals ──────────────────────────────────────────────────────────────────

class Deal(models.Model):
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='deals', null=True, blank=True)
    platform_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cashback = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True, default='')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)
    deal_score = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_demo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['-deal_score']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.title} — {self.platform_name}"


# ─── Events & Offers ────────────────────────────────────────────────────────

class PlatformEvent(models.Model):
    """Sales, festivals, and special offers from platforms (demo/sample data)."""

    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    platform_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    main_benefit = models.CharField(max_length=150, help_text='Primary discount or benefit headline')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    event_type = models.CharField(max_length=30, default='live_offer', choices=[
        ('festival', 'Festival Sale'),
        ('flash_sale', 'Flash Sale'),
        ('live_offer', 'Live Offer'),
        ('platform_offer', 'Platform Offer'),
        ('upcoming', 'Upcoming Event'),
    ])
    is_active = models.BooleanField(default=True)
    is_demo = models.BooleanField(default=True, help_text='Sample event for demo/presentation')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['platform_name', 'is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['starts_at']),
            models.Index(fields=['ends_at']),
        ]
        verbose_name = 'Platform event'
        verbose_name_plural = 'Platform events'

    def __str__(self):
        return f"{self.title} ({self.platform_name})"

    @property
    def status_label(self):
        now = timezone.now()
        if now < self.starts_at:
            return 'upcoming'
        if now > self.ends_at:
            return 'ended'
        days_left = (self.ends_at - now).days
        if days_left <= 3:
            return 'ending_soon'
        return 'live'

    @property
    def event_type_label(self):
        return dict(self._meta.get_field('event_type').choices).get(self.event_type, self.event_type)


# ─── Wallet ─────────────────────────────────────────────────────────────────

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    reward_points = models.IntegerField(default=0)
    cashback_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_credits = models.IntegerField(default=0)
    marketplace_earnings = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet: {self.user.username}"


class WalletTransaction(models.Model):
    TXN_TYPES = [
        ('earned', 'Earned'),
        ('spent', 'Spent'),
        ('received', 'Received'),
        ('sold', 'Sold'),
        ('purchased', 'Purchased'),
        ('refunded', 'Refunded'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    txn_type = models.CharField(max_length=20, choices=TXN_TYPES)
    points_delta = models.IntegerField(default=0)
    cashback_delta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['wallet', '-created_at'])]

    def __str__(self):
        return f"{self.txn_type}: {self.description}"


# ─── User preferences & behavior ────────────────────────────────────────────

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    favorite_categories = models.JSONField(default=list, blank=True)
    favorite_platforms = models.JSONField(default=list, blank=True)
    max_price_preference = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notify_price_drops = models.BooleanField(default=True)
    notify_coupon_expiry = models.BooleanField(default=True)
    notify_deals = models.BooleanField(default=True)
    notify_marketplace = models.BooleanField(default=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Preferences: {self.user.username}"


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches', null=True, blank=True)
    query = models.CharField(max_length=500)
    category = models.CharField(max_length=50)
    detected_category = models.CharField(max_length=50, blank=True, default='')
    result_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['user', '-created_at'])]
        verbose_name_plural = 'Search histories'

    def __str__(self):
        return self.query[:50]


# ─── Wishlist & Price Alerts ─────────────────────────────────────────────────

class WishlistItem(models.Model):
    ITEM_TYPES = [
        ('product', 'Product'),
        ('service', 'Service'),
        ('coupon', 'Coupon'),
        ('deal', 'Deal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='product')
    title = models.CharField(max_length=255)
    platform = models.CharField(max_length=100, blank=True, default='')
    category = models.CharField(max_length=50, blank=True, default='')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    previous_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reference_id = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['user', '-created_at'])]

    def __str__(self):
        return f"{self.user.username} — {self.title}"


class PriceAlert(models.Model):
    ALERT_TYPES = [
        ('price_drop', 'Price Drop'),
        ('coupon_expiry', 'Coupon Expiry'),
        ('deal_expiry', 'Deal Expiry'),
        ('new_offer', 'New Offer'),
        ('event_start', 'Event Starting'),
    ]
    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('price_dropped', 'Price Dropped'),
        ('offer_available', 'Offer Available'),
        ('expired', 'Expired'),
        ('triggered', 'Triggered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='price_drop')
    title = models.CharField(max_length=255)
    platform = models.CharField(max_length=100, blank=True, default='')
    category = models.CharField(max_length=50, blank=True, default='')
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='watching')
    wishlist_item = models.ForeignKey(
        'WishlistItem', on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts',
    )
    reference_id = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['target_price']),
            models.Index(fields=['alert_type']),
        ]

    def __str__(self):
        return f"{self.title} @ ₹{self.target_price}"

    @property
    def potential_savings(self):
        if self.current_price and self.target_price and self.current_price > self.target_price:
            return self.current_price - self.target_price
        return 0

    @property
    def alert_message(self):
        if self.status == 'price_dropped' and self.potential_savings:
            return f"Price Drop Alert! You can now save ₹{self.potential_savings:.0f}."
        if self.alert_type == 'coupon_expiry':
            return 'Coupon expiry reminder — use or sell before it expires.'
        if self.alert_type == 'deal_expiry':
            return 'Deal ending soon — compare prices before it expires.'
        if self.alert_type == 'event_start':
            return 'Event starting soon — check offers now.'
        return f'Watching for target price ₹{self.target_price}'


# ─── Notifications ───────────────────────────────────────────────────────────

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('price_drop', 'Price Drop'),
        ('coupon_expiring', 'Coupon Expiring'),
        ('coupon_sold', 'Coupon Sold'),
        ('coupon_purchased', 'Coupon Purchased'),
        ('reward_earned', 'Reward Earned'),
        ('order_completed', 'Order Completed'),
        ('new_deal', 'New Deal'),
        ('marketplace', 'Marketplace Activity'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='system')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'is_read', '-created_at'])]

    def __str__(self):
        return self.title


# ─── Reward Rules (configurable) ────────────────────────────────────────────

class RewardRule(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    points = models.IntegerField(validators=[MinValueValidator(0)])
    description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (+{self.points} pts)"
