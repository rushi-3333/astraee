from django.contrib import admin
from ASTRAEUser.models import (
    Order, Reward, UserCoupon, Category, Platform, Deal,
    Wallet, WalletTransaction, UserPreference, SearchHistory,
    WishlistItem, PriceAlert, Notification, RewardRule,
)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'category', 'item_title', 'final_price', 'status', 'created_at')
    list_filter = ('category', 'platform', 'status')
    search_fields = ('item_title', 'platform', 'user__username')


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'points_earned', 'description', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'coupon_code', 'status', 'is_for_sale', 'is_demo', 'granted_at')
    list_filter = ('platform', 'status', 'is_for_sale', 'is_demo')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'integration_type', 'status', 'api_status')
    list_filter = ('integration_type', 'status', 'category')


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform_name', 'category', 'final_price', 'deal_score', 'is_active')
    list_filter = ('category', 'is_active', 'is_demo')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward_points', 'cashback_balance', 'updated_at')


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'txn_type', 'points_delta', 'description', 'created_at')
    list_filter = ('txn_type',)


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'category', 'created_at')


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'platform', 'current_price', 'item_type')


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'target_price', 'current_price', 'status')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')


@admin.register(RewardRule)
class RewardRuleAdmin(admin.ModelAdmin):
    list_display = ('key', 'name', 'points', 'is_active')
