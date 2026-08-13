from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from ASTRAEUser.models import Order, UserCoupon, Reward
import json

@staff_member_required
def adminhome(request):
    users = User.objects.filter(is_staff=False, is_superuser=False)
    
    # 1. Metric Counts
    total_users_count = users.count()
    total_orders_count = Order.objects.count()
    total_coupons_count = UserCoupon.objects.count()
    marketplace_listed_count = UserCoupon.objects.filter(is_for_sale=True, is_used=False).count()

    # 2. Orders Breakdown by Category
    category_counts = Order.objects.values('category').annotate(total=Count('id'))
    category_data = {c['category']: c['total'] for c in category_counts}
    
    cat_labels = ['Rides', 'Food', 'Shopping', 'Medicine']
    cat_values = [
        category_data.get('ride', 0),
        category_data.get('food', 0),
        category_data.get('shopping', 0),
        category_data.get('medicine', 0),
    ]

    # 3. Top Platforms Distribution
    platform_counts = Order.objects.values('platform').annotate(total=Count('id')).order_by('-total')[:5]
    platform_labels = [p['platform'] for p in platform_counts]
    platform_values = [p['total'] for p in platform_counts]

    context = {
        'users': users,
        'total_users_count': total_users_count,
        'total_orders_count': total_orders_count,
        'total_coupons_count': total_coupons_count,
        'marketplace_listed_count': marketplace_listed_count,
        'cat_labels_json': json.dumps(cat_labels),
        'cat_values_json': json.dumps(cat_values),
        'platform_labels_json': json.dumps(platform_labels),
        'platform_values_json': json.dumps(platform_values),
    }
    return render(request, "Admin/adminhome.html", context)

@staff_member_required
def admin_update_userstatus(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        # Toggle the is_active status
        user.is_active = not user.is_active
        user.save()

        # Display message based on the action
        if user.is_active:
            messages.success(request, f"User {user.username} has been activated.")
        else:
            messages.success(request, f"User {user.username} has been deactivated.")
        
        return redirect('adminhome')  # Redirect back to the admin home page
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('adminhome')

@staff_member_required
def admin_orders_log(request):
    """View all completed orders filtered by domain category."""
    category = request.GET.get('category', 'all')
    if category != 'all':
        orders = Order.objects.filter(category=category).order_by('-created_at')
    else:
        orders = Order.objects.all().order_by('-created_at')

    context = {
        'orders': orders,
        'active_category': category,
        'total_count': orders.count()
    }
    return render(request, "Admin/admin_orders.html", context)

@staff_member_required
def admin_issued_coupons_log(request):
    """View all coupons issued by system to users upon order placement."""
    coupons = UserCoupon.objects.all().order_by('-granted_at')
    return render(request, "Admin/admin_issued_coupons.html", {'coupons': coupons})

@staff_member_required
def admin_open_sale_coupons_log(request):
    """View coupons currently listed for sale in P2P Marketplace."""
    coupons = UserCoupon.objects.filter(is_for_sale=True, is_used=False).order_by('-listed_at')
    return render(request, "Admin/admin_open_sale_coupons.html", {'coupons': coupons})

@staff_member_required
def admin_marketplace_sales_log(request):
    """View completed P2P marketplace transaction history."""
    sales_history = Reward.objects.filter(description__icontains="Purchased coupon").order_by('-created_at')
    return render(request, "Admin/admin_marketplace_sales.html", {'sales_history': sales_history})