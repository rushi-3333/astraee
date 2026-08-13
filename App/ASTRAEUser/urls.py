from django.urls import path
from ASTRAEUser import views

urlpatterns = [
    # Home & Search
    path('userhome/', views.userhome, name='userhome'),
    path('usersearch/', views.usersearch, name='usersearch'),
    path('userdeals/', views.userdeals, name='userdeals'),
    path('userevents/', views.userevents, name='userevents'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),

    # Orders & Booking
    path('userorders/', views.userorders, name='userorders'),
    path('orders/<int:order_id>/reschedule/', views.reschedule_order, name='reschedule_order'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('book/', views.book_offer, name='book_offer'),
    path('place_order/', views.place_order, name='place_order'),

    # Coupons & Marketplace
    path('usercoupons/', views.usercoupons, name='usercoupons'),
    path('sell_coupon/<int:coupon_id>/', views.sell_coupon, name='sell_coupon'),
    path('buy_coupon/<int:coupon_id>/', views.buy_coupon, name='buy_coupon'),
    path('add_coupon/', views.add_coupon, name='add_coupon'),

    # Rewards & Wallet
    path('userrewards/', views.userrewards, name='userrewards'),
    path('usersavings/', views.usersavings, name='usersavings'),

    # Wishlist & Alerts
    path('userwishlist/', views.userwishlist, name='userwishlist'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('useralerts/', views.useralerts, name='useralerts'),
    path('create_price_alert/', views.create_price_alert, name='create_price_alert'),
    path('delete_price_alert/<int:alert_id>/', views.delete_price_alert, name='delete_price_alert'),
    path('wishlist/<int:item_id>/alert/', views.wishlist_create_alert, name='wishlist_create_alert'),

    # Notifications
    path('usernotifications/', views.usernotifications, name='usernotifications'),
    path('mark_notifications_read/', views.mark_notifications_read, name='mark_notifications_read'),

    # Profile
    path('userprofile/', views.userprofile, name='userprofile'),
    path('update_profile/', views.update_profile, name='update_profile'),

    # JSON APIs
    path('api/search/', views.api_search, name='api_search'),
    path('api/deals/', views.api_deals, name='api_deals'),
    path('api/coupon-price/', views.api_coupon_price_suggestion, name='api_coupon_price'),
]
