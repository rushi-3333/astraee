from django.urls import path
from ASTRAEAdmin import views

urlpatterns = [
    path('adminhome/', views.adminhome, name='adminhome'),
    path('admin_update_userstatus/<int:user_id>/', views.admin_update_userstatus, name='admin_update_userstatus'),
    path('admin_orders/', views.admin_orders_log, name='admin_orders_log'),
    path('admin_issued_coupons/', views.admin_issued_coupons_log, name='admin_issued_coupons_log'),
    path('admin_open_sale_coupons/', views.admin_open_sale_coupons_log, name='admin_open_sale_coupons_log'),
    path('admin_marketplace_sales/', views.admin_marketplace_sales_log, name='admin_marketplace_sales_log'),
]