from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from ASTRAEUser.services.admin_analytics_service import get_admin_dashboard_metrics


@staff_member_required
def adminhome(request):
    users = User.objects.filter(is_staff=False, is_superuser=False)
    metrics = get_admin_dashboard_metrics()
    context = {'users': users, **metrics}
    return render(request, "Admin/adminhome.html", context)

@staff_member_required
@require_POST
def admin_update_userstatus(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        if user.is_active:
            messages.success(request, f"User {user.username} has been activated.")
        else:
            messages.success(request, f"User {user.username} has been deactivated.")
        return redirect('adminhome')
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('adminhome')

@staff_member_required
def admin_orders_log(request):
    from ASTRAEUser.models import Order
    category = request.GET.get('category', 'all')
    if category != 'all':
        orders = Order.objects.filter(category=category).order_by('-created_at')
    else:
        orders = Order.objects.all().order_by('-created_at')
    context = {'orders': orders, 'active_category': category, 'total_count': orders.count()}
    return render(request, "Admin/admin_orders.html", context)

@staff_member_required
def admin_issued_coupons_log(request):
    from ASTRAEUser.models import UserCoupon
    coupons = UserCoupon.objects.all().order_by('-granted_at')
    return render(request, "Admin/admin_issued_coupons.html", {'coupons': coupons})

@staff_member_required
def admin_open_sale_coupons_log(request):
    from ASTRAEUser.models import UserCoupon
    coupons = UserCoupon.objects.filter(is_for_sale=True, is_used=False).order_by('-listed_at')
    return render(request, "Admin/admin_open_sale_coupons.html", {'coupons': coupons})

@staff_member_required
def admin_marketplace_sales_log(request):
    from ASTRAEUser.models import Reward
    sales_history = Reward.objects.filter(description__icontains="Sold coupon").order_by('-created_at')
    return render(request, "Admin/admin_marketplace_sales.html", {'sales_history': sales_history})
