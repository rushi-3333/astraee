from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum
from django.utils import timezone
from .models import Order, Reward, UserCoupon
from .services.order_service import process_booking
from .services.ride_service import search_rides
from .services.food_service import search_food
from .services.shopping_service import search_shopping
from .services.medicine_service import search_medicine
from .services.comparison_service import execute_unified_search

# Create your views here.
def userhome(request):
    user = request.user

    if user.is_authenticated:
        # 1. Total Reward Points Balance
        total_points = Reward.objects.filter(user=user).aggregate(
            Sum('points_earned')
        )['points_earned__sum'] or 0

        # 2. Total Orders Completed & Cumulative Estimated Savings
        user_orders = Order.objects.filter(user=user).order_by('-created_at')
        total_orders_count = user_orders.count()
        
        # Estimate savings: ~15% saved average across all ASTRAE comparisons
        total_spent = user_orders.aggregate(Sum('final_price'))['final_price__sum'] or 0
        estimated_savings = round(float(total_spent) * 0.15, 2)

        # 3. Active Coupons Inventory (Unused)
        active_coupons = UserCoupon.objects.filter(user=user, is_used=False).order_by('-granted_at')
        active_coupons_count = active_coupons.count()
        recent_coupons = active_coupons[:3]  # Top 3 latest issued

        # 4. Recent Order History (Latest 5 orders)
        recent_orders = user_orders[:5]
    else:
        total_points = 0
        total_orders_count = 0
        estimated_savings = 0.0
        active_coupons_count = 0
        recent_coupons = []
        recent_orders = []

    context = {
        'user': user,
        'total_points': total_points,
        'total_orders_count': total_orders_count,
        'estimated_savings': estimated_savings,
        'active_coupons_count': active_coupons_count,
        'recent_coupons': recent_coupons,
        'recent_orders': recent_orders,
    }
    return render(request, 'User/userhome.html', context)

def usersearch(request):
    category = request.GET.get('category', 'ride')
    query1 = request.GET.get('q1', '').strip()  # Pickup / Location / Deliver to
    query2 = request.GET.get('q2', '').strip()  # Destination / Craving / Product / Medicine
    sort_by = request.GET.get('sort_by', 'lowest_price')
    max_price = request.GET.get('max_price', None)
    min_rating = request.GET.get('min_rating', None)

    # Set smart defaults if inputs are empty
    if not query1 and not query2:
        if category == 'ride':
            q_from, q_to = "Gachibowli", "Hitech City"
        elif category == 'food':
            q_from, q_to = "Hyderabad", "Chicken Biryani"
        elif category == 'shopping':
            q_from, q_to = "Hyderabad", "iPhone 15 128GB"
        elif category == 'medicine':
            q_from, q_to = "Hyderabad", "Dolo 650"
    else:
        q_from = query1
        q_to = query2

    # Step 1, 2, 3: Retrieve via ChromaDB & Predict via AEECF CatBoost
    search_output = execute_unified_search(category, q_from, q_to)
    all_candidates = search_output.get('all_results', [])

    # Step 4: Apply UI Filters (Price & Rating)
    if max_price:
        try:
            max_p = float(max_price)
            all_candidates = [r for r in all_candidates if r['final_price'] <= max_p]
        except ValueError:
            pass

    if min_rating and min_rating != 'Any':
        try:
            min_r = float(min_rating.replace('+', ''))
            all_candidates = [r for r in all_candidates if r['rating'] >= min_r]
        except ValueError:
            pass

    # Step 5: Apply UI Sorting
    if sort_by == 'lowest_price':
        all_candidates = sorted(all_candidates, key=lambda x: x['final_price'])
    elif sort_by == 'fastest':
        all_candidates = sorted(all_candidates, key=lambda x: x['eta_mins'])
    elif sort_by == 'rating':
        all_candidates = sorted(all_candidates, key=lambda x: x['rating'], reverse=True)

    # Extract top recommendation and secondary options
    recommended = all_candidates[0] if all_candidates else None
    other_results = all_candidates[1:] if len(all_candidates) > 1 else []

    context = {
        'active_category': category,
        'q1': query1,
        'q2': query2,
        'sort_by': sort_by,
        'recommended': recommended,
        'results': other_results,
        'total_count': len(all_candidates),
    }
    return render(request, 'User/usersearch.html', context)

@login_required
def userprofile(request):
    user = request.user

    # Aggregate user metrics for the profile summary
    total_orders = Order.objects.filter(user=user).count()
    total_points = Reward.objects.filter(user=user).aggregate(
        Sum('points_earned')
    )['points_earned__sum'] or 0
    active_coupons = UserCoupon.objects.filter(user=user, is_used=False).count()

    context = {
        'user': user,
        'total_orders': total_orders,
        'total_points': total_points,
        'active_coupons': active_coupons,
    }
    return render(request, 'User/userprofile.html', context)


@login_required
def update_profile(request):
    """Handles updating registration details (first_name, last_name, email, password)."""
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        new_password = request.POST.get('new_password', '').strip()

        # Update basic info
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        # Optional password update
        if new_password:
            user.set_password(new_password)
            user.save()
            # Keep user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, "Profile details and password updated successfully!")
        else:
            user.save()
            messages.success(request, "Profile details updated successfully!")

        return redirect('userprofile')

    return redirect('userprofile')

def place_order(request):
    """Handles 'Book now' and 'Select Platform' form submissions."""
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please login to place an order.")
            return redirect('loginn')

        platform = request.POST.get('platform', 'ASTRAE Partner')
        category = request.POST.get('category', 'ride')
        item_title = request.POST.get('item_title', 'Service Booking')
        final_price = request.POST.get('final_price', '100.0')

        # Execute booking workflow
        order, reward, coupon = process_booking(
            user=request.user,
            platform=platform,
            category=category,
            item_title=item_title,
            final_price=final_price
        )

        messages.success(
            request, 
            f"🎉 Order placed successfully on {platform}! "
            f"You earned +{reward.points_earned} ASTRAE Reward Points and a new coupon '{coupon.coupon_code}'."
        )
        return redirect('usercoupons')

    return redirect('usersearch')

def usercoupons(request):
    if request.user.is_authenticated:
        # 1. User's personal coupons (owned and active)
        my_coupons = UserCoupon.objects.filter(
            user=request.user, 
            is_used=False
        ).order_by('-granted_at')

        # 2. Marketplace coupons (listed for sale by OTHER users)
        marketplace_coupons = UserCoupon.objects.filter(
            is_for_sale=True, 
            is_used=False
        ).exclude(user=request.user).order_by('-listed_at')

        # 3. User total points balance
        user_points = Reward.objects.filter(user=request.user).aggregate(
            Sum('points_earned')
        )['points_earned__sum'] or 0
    else:
        my_coupons = []
        marketplace_coupons = []
        user_points = 0

    context = {
        'my_coupons': my_coupons,
        'marketplace_coupons': marketplace_coupons,
        'user_points': user_points
    }
    return render(request, 'User/usercoupons.html', context)


@login_required
def sell_coupon(request, coupon_id):
    """Puts an owned coupon up for sale on the marketplace."""
    if request.method == "POST":
        coupon = get_object_or_404(UserCoupon, id=coupon_id, user=request.user)
        price_pts = int(request.POST.get('price_in_points', 50))

        coupon.is_for_sale = True
        coupon.price_in_points = max(10, price_pts)
        coupon.listed_at = timezone.now()
        coupon.save()

        messages.success(request, f"Coupon '{coupon.coupon_code}' is now listed on the marketplace for {coupon.price_in_points} PTS!")
    return redirect('usercoupons')


@login_required
def buy_coupon(request, coupon_id):
    """Allows a user to purchase a listed coupon using reward points."""
    if request.method == "POST":
        coupon = get_object_or_404(UserCoupon, id=coupon_id, is_for_sale=True, is_used=False)
        seller = coupon.user
        buyer = request.user

        if seller == buyer:
            messages.error(request, "You cannot buy your own listed coupon.")
            return redirect('usercoupons')

        # Check buyer total points balance
        buyer_points = Reward.objects.filter(user=buyer).aggregate(Sum('points_earned'))['points_earned__sum'] or 0

        if buyer_points < coupon.price_in_points:
            messages.error(request, f"Insufficient balance! You need {coupon.price_in_points} PTS but have {buyer_points} PTS.")
            return redirect('usercoupons')

        # 1. Deduct points from buyer
        Reward.objects.create(
            user=buyer,
            points_earned=-coupon.price_in_points,
            description=f"Purchased coupon '{coupon.coupon_code}' ({coupon.platform}) from {seller.username}"
        )

        # 2. Credit points to seller
        Reward.objects.create(
            user=seller,
            points_earned=coupon.price_in_points,
            description=f"Sold coupon '{coupon.coupon_code}' ({coupon.platform}) to {buyer.username}"
        )

        # 3. Transfer ownership and unlist from marketplace
        coupon.user = buyer
        coupon.is_for_sale = False
        coupon.listed_at = None
        coupon.save()

        messages.success(request, f"🎉 Successfully purchased coupon '{coupon.coupon_code}' for {coupon.price_in_points} PTS! It is now in your inventory.")
    return redirect('usercoupons')

def userrewards(request):
    if request.user.is_authenticated:
        reward_history = Reward.objects.filter(user=request.user).order_by('-created_at')
        total_points = Reward.objects.filter(user=request.user).aggregate(
            Sum('points_earned')
        )['points_earned__sum'] or 0
        total_orders = Order.objects.filter(user=request.user).count()
    else:
        reward_history = []
        total_points = 0
        total_orders = 0

    context = {
        'reward_history': reward_history,
        'total_points': total_points,
        'total_orders': total_orders
    }
    return render(request, 'User/userrewards.html', context)