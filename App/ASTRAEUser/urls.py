from django.urls import path
from ASTRAEUser.views import userhome, usercoupons, usersearch, userprofile, userrewards, place_order, sell_coupon, buy_coupon, update_profile

urlpatterns = [
    path('userhome/', userhome, name='userhome'),
    path('usersearch/', usersearch, name='usersearch'),
    path('usercoupons/', usercoupons, name='usercoupons'),
    path('userrewards/', userrewards, name='userrewards'),
    path('userprofile/', userprofile, name='userprofile'),
    path('update_profile/', update_profile, name='update_profile'),
    path('place_order/', place_order, name='place_order'),
    path('sell_coupon/<int:coupon_id>/', sell_coupon, name='sell_coupon'),
    path('buy_coupon/<int:coupon_id>/', buy_coupon, name='buy_coupon'),

]