from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    platform = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    item_title = models.CharField(max_length=255)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.platform} ({self.item_title})"

class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
    points_earned = models.IntegerField(default=50)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.points_earned} Points"

class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupons')
    platform = models.CharField(max_length=100)
    coupon_code = models.CharField(max_length=50)
    discount_text = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)
    
    # Marketplace Fields
    is_for_sale = models.BooleanField(default=False)
    price_in_points = models.IntegerField(default=50)
    listed_at = models.DateTimeField(null=True, blank=True)
    granted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.coupon_code} ({self.platform})"