from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum, Count
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from datetime import timedelta, date
import json

from .models import (
    Order, Reward, UserCoupon, Deal, WishlistItem, PriceAlert,
    Notification, UserPreference, SearchHistory, Platform, Category,
    PlatformEvent,
)
from .services.order_service import process_booking
from .services.unified_search_service import execute_smart_search
from .services.search_service import detect_category
from .services.deals_service import get_deals, compute_deal_score
from .services.events_service import get_events, get_event_counts, PLATFORM_COLORS
from .services.wallet_service import get_wallet_summary, sync_wallet_from_rewards
from .services.reward_service import grant_reward, get_rule_points, ensure_default_rules
from .services.coupon_verifier import verify_and_update_coupon, DemoCouponVerifier
from .services.coupon_pricing_service import suggest_coupon_price
from .services.personalization_service import get_personalized_recommendations
from .services.notification_service import get_unread_count, mark_all_read, create_notification
from .services.api_helpers import api_success, api_error


# ─── HOME ────────────────────────────────────────────────────────────────────

def userhome(request):
    user = request.user
    rec_data = get_personalized_recommendations(user)
    recommendations = []
    for msg in rec_data.get('messages', []):
        recommendations.append({
            'type': msg.get('type', 'tip').title(),
            'title': msg.get('text', '')[:60],
            'reason': msg.get('text', ''),
            'link': f"/ASTRAEUser/userdeals/?category={rec_data.get('top_category', '')}",
        })
    for deal in rec_data.get('deals', [])[:3]:
        recommendations.append({
            'type': 'Deal',
            'title': deal.title,
            'reason': f'{deal.platform_name} — ₹{deal.final_price} (Score {deal.deal_score})',
            'link': f'/ASTRAEUser/userdeals/?category={deal.category}',
        })

    if user.is_authenticated:
        total_points = Reward.objects.filter(user=user).aggregate(Sum('points_earned'))['points_earned__sum'] or 0
        user_orders = Order.objects.filter(user=user).order_by('-created_at')
        total_orders_count = user_orders.count()
        total_spent = user_orders.aggregate(Sum('final_price'))['final_price__sum'] or 0
        estimated_savings = round(float(total_spent) * 0.15, 2)
        active_coupons = UserCoupon.objects.filter(user=user, is_used=False).order_by('-granted_at')
        active_coupons_count = active_coupons.count()
        recent_coupons = active_coupons[:4]
        recent_orders = user_orders[:5]
        recent_searches = SearchHistory.objects.filter(user=user).order_by('-created_at')[:5]
    else:
        total_points = 0
        total_orders_count = 0
        estimated_savings = 0.0
        active_coupons_count = 0
        recent_coupons = []
        recent_orders = []
        recent_searches = []

    trending_deals = list(Deal.objects.filter(is_active=True).order_by('-deal_score')[:8])
    popular_coupons = UserCoupon.objects.filter(is_for_sale=True, is_used=False, status='listed')[:6]
    categories = Category.objects.filter(is_active=True)[:8]

    context = {
        'user': user,
        'total_points': total_points,
        'total_orders_count': total_orders_count,
        'estimated_savings': estimated_savings,
        'active_coupons_count': active_coupons_count,
        'recent_coupons': recent_coupons,
        'recent_orders': recent_orders,
        'trending_deals': trending_deals,
        'popular_coupons': popular_coupons,
        'categories': categories,
        'recommendations': recommendations,
        'recent_searches': recent_searches,
        'unread_notifications': get_unread_count(user),
        'category_list': [
            ('ride', 'Rides', '🚗'), ('food', 'Food', '🍔'), ('grocery', 'Grocery', '🛒'),
            ('shopping', 'Shopping', '🛍️'), ('fashion', 'Fashion', '👗'), ('beauty', 'Beauty', '💄'),
            ('medicine', 'Medicine', '💊'),
        ],
        'how_it_works': [
            ('1', 'Search once', 'Enter what you need — rides, food, products or medicine.'),
            ('2', 'Compare all', 'See prices, ratings, cashback & ASTRAE Score side by side.'),
            ('3', 'Book & save', 'Pick the best value option and complete your order.'),
            ('4', 'Earn more', 'Get rewards, trade coupons, and track your savings.'),
        ],
    }
    return render(request, 'User/userhome.html', context)


# ─── COMPARE / SEARCH ────────────────────────────────────────────────────────

def usersearch(request):
    unified_query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    query1 = request.GET.get('q1', '').strip()
    query2 = request.GET.get('q2', '').strip()
    sort_by = request.GET.get('sort_by', 'best_value')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('min_rating')

    if unified_query and not query1:
        category, query1, query2 = detect_category(unified_query)

    if not category:
        category = 'ride'

    if not query1 and not query2:
        defaults = {
            'ride': ('Hitech City', 'Gachibowli'),
            'food': ('Hyderabad', 'Chicken Biryani'),
            'grocery': ('Hyderabad', 'Groceries under ₹1000'),
            'shopping': ('Hyderabad', 'iPhone 16'),
            'medicine': ('Hyderabad', 'Medicine for cold'),
            'fashion': ('Hyderabad', 'Sneakers'),
            'beauty': ('Hyderabad', 'Skincare'),
        }
        query1, query2 = defaults.get(category, ('Hyderabad', 'Product'))

    search_output = execute_smart_search(category, query1, query2)
    all_candidates = search_output.get('all_results', [])

    if max_price:
        try:
            all_candidates = [r for r in all_candidates if r['final_price'] <= float(max_price)]
        except ValueError:
            pass
    if min_rating and min_rating != 'Any':
        try:
            min_r = float(min_rating.replace('+', ''))
            all_candidates = [r for r in all_candidates if r['rating'] >= min_r]
        except ValueError:
            pass

    sort_keys = {
        'lowest_price': lambda x: x['final_price'],
        'fastest': lambda x: x['eta_mins'],
        'rating': lambda x: -x['rating'],
        'best_value': lambda x: -x.get('astrae_score', 0),
    }
    all_candidates = sorted(all_candidates, key=sort_keys.get(sort_by, sort_keys['best_value']))

    if request.user.is_authenticated and (unified_query or query2):
        SearchHistory.objects.create(
            user=request.user,
            query=unified_query or f"{query1} {query2}",
            category=category,
            detected_category=category,
            result_count=len(all_candidates),
        )

    recommended = all_candidates[0] if all_candidates else None
    other_results = all_candidates[1:] if len(all_candidates) > 1 else []

    context = {
        'active_category': category,
        'q': unified_query,
        'q1': query1,
        'q2': query2,
        'sort_by': sort_by,
        'recommended': recommended,
        'results': other_results,
        'total_count': len(all_candidates),
        'highlights': search_output.get('highlights', {}),
        'unread_notifications': get_unread_count(request.user),
        'categories_list': [
            ('ride', 'Rides', '🚗'), ('food', 'Food', '🍔'), ('grocery', 'Grocery', '🛒'),
            ('shopping', 'Shopping', '🛍️'), ('fashion', 'Fashion', '👗'), ('beauty', 'Beauty', '💄'),
            ('medicine', 'Medicine', '💊'),
        ],
    }
    if request.user.is_authenticated:
        context['recent_searches'] = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]
    else:
        context['recent_searches'] = []
    return render(request, 'User/usersearch.html', context)


# ─── DEALS ───────────────────────────────────────────────────────────────────

def userdeals(request):
    category = request.GET.get('category', '')
    platform = request.GET.get('platform', '')
    sort_by = request.GET.get('sort_by', 'best_deal')
    deals = get_deals(
        filters={'category': category, 'platform': platform,
                 'min_discount': request.GET.get('min_discount'),
                 'max_price': request.GET.get('max_price')},
        sort_by=sort_by,
    )
    categories = Category.objects.filter(is_active=True)
    platforms = Platform.objects.filter(status='active')[:20]
    context = {
        'deals': deals,
        'categories': categories,
        'platforms': platforms,
        'active_category': category,
        'active_platform': platform,
        'sort_by': sort_by,
        'unread_notifications': get_unread_count(request.user),
    }
    return render(request, 'User/userdeals.html', context)


# ─── EVENTS & OFFERS ─────────────────────────────────────────────────────────

def userevents(request):
    platform = request.GET.get('platform', '')
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')

    events = get_events(filters={
        'platform': platform,
        'category': category,
        'status': status,
    })
    event_counts = get_event_counts()

    # Attach platform logo colors for template
    for event in events:
        color, initial = PLATFORM_COLORS.get(event.platform_name, ('#4F46E5', event.platform_name[:2]))
        event.logo_color = color
        event.logo_initial = initial

    context = {
        'events': events,
        'event_counts': event_counts,
        'active_platform': platform,
        'active_category': category,
        'active_status': status,
        'categories': Category.objects.filter(is_active=True),
        'platforms': Platform.objects.filter(
            name__in=['Amazon', 'Flipkart', 'Myntra', 'Ajio', 'BigBasket', 'Zepto',
                      'Blinkit', 'Swiggy', 'Zomato', 'Nykaa']
        ).order_by('name'),
        'platform_colors': PLATFORM_COLORS,
        'unread_notifications': get_unread_count(request.user),
    }
    return render(request, 'User/userevents.html', context)


# ─── ORDERS ──────────────────────────────────────────────────────────────────

@login_required
def userorders(request):
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    if status_filter:
        orders = orders.filter(status=status_filter)
    if category_filter:
        orders = orders.filter(category=category_filter)
    context = {
        'orders': orders,
        'active_status': status_filter,
        'active_category': category_filter,
        'unread_notifications': get_unread_count(request.user),
    }
    return render(request, 'User/userorders.html', context)


# ─── WISHLIST ────────────────────────────────────────────────────────────────

@login_required
def userwishlist(request):
    items = WishlistItem.objects.filter(user=request.user).order_by('-created_at')
    context = {'wishlist_items': items, 'unread_notifications': get_unread_count(request.user)}
    return render(request, 'User/userwishlist.html', context)


@login_required
@require_POST
def add_to_wishlist(request):
    WishlistItem.objects.create(
        user=request.user,
        item_type=request.POST.get('item_type', 'product'),
        title=request.POST.get('title', 'Saved Item'),
        platform=request.POST.get('platform', ''),
        category=request.POST.get('category', ''),
        current_price=request.POST.get('current_price', 0) or 0,
        lowest_price=request.POST.get('current_price', 0) or 0,
    )
    messages.success(request, 'Added to wishlist!')
    return redirect(request.POST.get('next', 'userwishlist'))


@login_required
@require_POST
def remove_from_wishlist(request, item_id):
    WishlistItem.objects.filter(id=item_id, user=request.user).delete()
    messages.success(request, 'Removed from wishlist.')
    return redirect('userwishlist')


# ─── NOTIFICATIONS ───────────────────────────────────────────────────────────

@login_required
def usernotifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread = notifications.filter(is_read=False).count()
    context = {
        'notifications': notifications[:50],
        'unread_count': unread,
        'unread_notifications': unread,
    }
    return render(request, 'User/usernotifications.html', context)


@login_required
@require_POST
def mark_notifications_read(request):
    mark_all_read(request.user)
    messages.success(request, 'All notifications marked as read.')
    return redirect('usernotifications')


# ─── SAVINGS DASHBOARD ─────────────────────────────────────────────────────────

@login_required
def usersavings(request):
    orders = Order.objects.filter(user=request.user)
    total_spent = float(orders.aggregate(Sum('final_price'))['final_price__sum'] or 0)
    total_saved = float(orders.aggregate(Sum('astrae_savings'))['astrae_savings__sum'] or 0)
    total_points = Reward.objects.filter(user=request.user).aggregate(Sum('points_earned'))['points_earned__sum'] or 0

    category_spending = orders.values('category').annotate(
        total=Sum('final_price'), count=Count('id')
    ).order_by('-total')

    platform_usage = orders.values('platform').annotate(
        count=Count('id')
    ).order_by('-count')[:8]

    monthly = {}
    for o in orders:
        month_key = o.created_at.strftime('%Y-%m')
        if month_key not in monthly:
            monthly[month_key] = {'spent': 0, 'saved': 0}
        monthly[month_key]['spent'] += float(o.final_price)
        monthly[month_key]['saved'] += float(o.astrae_savings)

    marketplace_earnings = Reward.objects.filter(
        user=request.user, description__icontains='Sold coupon'
    ).aggregate(Sum('points_earned'))['points_earned__sum'] or 0

    context = {
        'total_spent': total_spent,
        'total_saved': total_saved or round(total_spent * 0.15, 2),
        'total_points': total_points,
        'marketplace_earnings': marketplace_earnings,
        'category_spending': list(category_spending),
        'platform_usage': list(platform_usage),
        'monthly_json': json.dumps(monthly),
        'category_json': json.dumps({c['category']: float(c['total']) for c in category_spending}),
        'unread_notifications': get_unread_count(request.user),
    }
    return render(request, 'User/usersavings.html', context)


# ─── PROFILE ─────────────────────────────────────────────────────────────────

@login_required
def userprofile(request):
    pref, _ = UserPreference.objects.get_or_create(user=request.user)
    total_orders = Order.objects.filter(user=request.user).count()
    total_points = Reward.objects.filter(user=request.user).aggregate(Sum('points_earned'))['points_earned__sum'] or 0
    active_coupons = UserCoupon.objects.filter(user=request.user, is_used=False).count()
    context = {
        'user': request.user,
        'preferences': pref,
        'total_orders': total_orders,
        'total_points': total_points,
        'active_coupons': active_coupons,
        'unread_notifications': get_unread_count(request.user),
    }
    return render(request, 'User/userprofile.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        new_password = request.POST.get('new_password', '').strip()

        pref, _ = UserPreference.objects.get_or_create(user=user)
        pref.phone = request.POST.get('phone', '').strip()
        pref.address = request.POST.get('address', '').strip()
        pref.favorite_categories = request.POST.getlist('favorite_categories')
        pref.favorite_platforms = request.POST.getlist('favorite_platforms')
        pref.notify_price_drops = 'notify_price_drops' in request.POST
        pref.notify_coupon_expiry = 'notify_coupon_expiry' in request.POST
        pref.notify_deals = 'notify_deals' in request.POST
        pref.save()

        if new_password:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Profile and password updated!')
        else:
            user.save()
            messages.success(request, 'Profile updated successfully!')
        return redirect('userprofile')
    return redirect('userprofile')


# ─── PLACE ORDER ─────────────────────────────────────────────────────────────

@login_required
def place_order(request):
    if request.method == 'POST':
        order, reward, coupon = process_booking(
            user=request.user,
            platform=request.POST.get('platform', 'ASTRAE Partner'),
            category=request.POST.get('category', 'ride'),
            item_title=request.POST.get('item_title', 'Service Booking'),
            final_price=request.POST.get('final_price', '100.0'),
            original_price=request.POST.get('original_price'),
            discount=request.POST.get('discount', 0),
            coupon_applied=request.POST.get('coupon', ''),
            cashback=request.POST.get('cashback', 0),
        )
        messages.success(
            request,
            f'Order placed on {order.platform}! +{reward.points_earned} points & coupon {coupon.coupon_code} earned.',
        )
        return redirect('userorders')
    return redirect('usersearch')


# ─── COUPONS / MARKETPLACE ───────────────────────────────────────────────────

def usercoupons(request):
    if request.user.is_authenticated:
        my_coupons = UserCoupon.objects.filter(user=request.user, is_used=False).order_by('-granted_at')
        marketplace_coupons = UserCoupon.objects.filter(
            is_for_sale=True, is_used=False, status__in=['listed', 'verified']
        ).exclude(user=request.user).order_by('-listed_at')
        user_points = Reward.objects.filter(user=request.user).aggregate(Sum('points_earned'))['points_earned__sum'] or 0
        sync_wallet_from_rewards(request.user)
    else:
        my_coupons = []
        marketplace_coupons = UserCoupon.objects.filter(is_for_sale=True, is_used=False)[:20]
        user_points = 0

    context = {
        'my_coupons': my_coupons,
        'marketplace_coupons': marketplace_coupons,
        'user_points': user_points,
        'unread_notifications': get_unread_count(request.user),
    }
    return render(request, 'User/usercoupons.html', context)


@login_required
@require_POST
def sell_coupon(request, coupon_id):
    coupon = get_object_or_404(UserCoupon, id=coupon_id, user=request.user)
    price_pts = int(request.POST.get('price_in_points', 50))
    face_value = float(request.POST.get('face_value', 500))
    days_expiry = int(request.POST.get('days_until_expiry', 30))

    suggestion = suggest_coupon_price(face_value, 100, days_expiry, coupon.platform)
    if price_pts < 10:
        price_pts = suggestion['suggested_price']

    verify_result = verify_and_update_coupon(coupon)
    if not verify_result['valid']:
        messages.error(request, verify_result['errors'][0])
        return redirect('usercoupons')

    coupon.is_for_sale = True
    coupon.price_in_points = max(10, price_pts)
    coupon.face_value = face_value
    coupon.status = 'listed'
    coupon.listed_at = timezone.now()
    coupon.save()

    messages.success(request, f"Coupon listed for {coupon.price_in_points} PTS. Suggested: {suggestion['suggested_price']} PTS.")
    return redirect('usercoupons')


@login_required
@require_POST
@transaction.atomic
def buy_coupon(request, coupon_id):
    coupon = get_object_or_404(UserCoupon, id=coupon_id, is_for_sale=True, is_used=False)
    seller = coupon.user
    buyer = request.user

    if seller == buyer:
        messages.error(request, 'You cannot buy your own coupon.')
        return redirect('usercoupons')

    if coupon.status not in ('listed', 'verified'):
        messages.error(request, 'This coupon is no longer available.')
        return redirect('usercoupons')

    if coupon.expiry_date and coupon.expiry_date < date.today():
        coupon.status = 'expired'
        coupon.save()
        messages.error(request, 'This coupon has expired.')
        return redirect('usercoupons')

    buyer_points = Reward.objects.filter(user=buyer).aggregate(Sum('points_earned'))['points_earned__sum'] or 0
    if buyer_points < coupon.price_in_points:
        messages.error(request, f'Insufficient balance! Need {coupon.price_in_points} PTS, have {buyer_points} PTS.')
        return redirect('usercoupons')

    coupon.status = 'reserved'
    coupon.save()

    grant_reward(buyer, -coupon.price_in_points,
                 f"Purchased coupon '{coupon.coupon_code}' ({coupon.platform}) from {seller.username}",
                 rule_key='marketplace_purchase')
    seller_bonus = get_rule_points('coupon_sold', 15)
    grant_reward(seller, coupon.price_in_points,
                 f"Sold coupon '{coupon.coupon_code}' ({coupon.platform}) to {buyer.username}",
                 rule_key='coupon_sold')
    if seller_bonus:
        grant_reward(seller, seller_bonus, f'Bonus for marketplace sale', rule_key='coupon_sold')

    coupon.user = buyer
    coupon.is_for_sale = False
    coupon.status = 'sold'
    coupon.listed_at = None
    coupon.save()

    create_notification(seller, 'coupon_sold', 'Coupon Sold!',
                        f'Your {coupon.platform} coupon was purchased for {coupon.price_in_points} PTS.',
                        '/ASTRAEUser/usercoupons/')
    create_notification(buyer, 'coupon_purchased', 'Coupon Purchased!',
                        f'You bought a {coupon.platform} coupon. Check your wallet.',
                        '/ASTRAEUser/usercoupons/')

    messages.success(request, f"Purchased coupon for {coupon.price_in_points} PTS!")
    return redirect('usercoupons')


@login_required
@require_POST
def add_coupon(request):
    platform = request.POST.get('platform', '').strip()
    code = request.POST.get('coupon_code', '').strip().upper()
    discount_text = request.POST.get('discount_text', 'Special Offer')
    face_value = float(request.POST.get('face_value', 500))
    days = int(request.POST.get('days_until_expiry', 30))

    verifier = DemoCouponVerifier()
    result = verifier.verify(platform, code, date.today() + timedelta(days=days))
    if not result['valid']:
        messages.error(request, result['errors'][0])
        return redirect('usercoupons')

    UserCoupon.objects.create(
        user=request.user,
        platform=platform,
        coupon_code=code,
        discount_text=discount_text,
        face_value=face_value,
        expiry_date=date.today() + timedelta(days=days),
        status='verified',
        is_demo=True,
    )
    messages.success(request, 'Coupon added and verified (demo mode).')
    return redirect('usercoupons')


# ─── REWARDS ─────────────────────────────────────────────────────────────────

def userrewards(request):
    ensure_default_rules()
    if request.user.is_authenticated:
        reward_history = Reward.objects.filter(user=request.user).order_by('-created_at')
        total_points = Reward.objects.filter(user=request.user).aggregate(Sum('points_earned'))['points_earned__sum'] or 0
        total_orders = Order.objects.filter(user=request.user).count()
        wallet = get_wallet_summary(request.user)
        redeemed = abs(sum(r.points_earned for r in reward_history if r.points_earned < 0))
        pending = reward_history.filter(status='pending').aggregate(Sum('points_earned'))['points_earned__sum'] or 0
    else:
        reward_history = []
        total_points = 0
        total_orders = 0
        wallet = {}
        redeemed = 0
        pending = 0

    context = {
        'reward_history': reward_history,
        'total_points': total_points,
        'total_orders': total_orders,
        'wallet': wallet,
        'redeemed_points': redeemed,
        'pending_points': pending,
        'unread_notifications': get_unread_count(request.user),
    }
    return render(request, 'User/userrewards.html', context)


# ─── PRICE ALERTS ────────────────────────────────────────────────────────────

@login_required
def useralerts(request):
    alerts = PriceAlert.objects.filter(user=request.user).order_by('-created_at')
    context = {'alerts': alerts, 'unread_notifications': get_unread_count(request.user)}
    return render(request, 'User/useralerts.html', context)


@login_required
@require_POST
def create_price_alert(request):
    PriceAlert.objects.create(
        user=request.user,
        title=request.POST.get('title', 'Product'),
        platform=request.POST.get('platform', ''),
        category=request.POST.get('category', 'shopping'),
        target_price=request.POST.get('target_price', 0),
        current_price=request.POST.get('current_price', 0),
    )
    messages.success(request, 'Price alert created!')
    return redirect('useralerts')


# ─── JSON APIs ───────────────────────────────────────────────────────────────

@require_GET
def api_search(request):
    q = request.GET.get('q', '')
    category, q1, q2 = detect_category(q) if q else ('ride', 'Hyderabad', 'Airport')
    if request.GET.get('category'):
        category = request.GET.get('category')
    if request.GET.get('q1'):
        q1, q2 = request.GET.get('q1'), request.GET.get('q2', '')
    result = execute_smart_search(category, q1, q2)
    return api_success(result)


@require_GET
def api_deals(request):
    deals = get_deals(filters={'category': request.GET.get('category', '')})
    data = [{'title': d.title, 'platform': d.platform_name, 'final_price': float(d.final_price),
             'deal_score': d.deal_score} for d in deals[:20]]
    return api_success(data)


@require_GET
def api_coupon_price_suggestion(request):
    try:
        suggestion = suggest_coupon_price(
            float(request.GET.get('face_value', 500)),
            float(request.GET.get('discount', 100)),
            int(request.GET.get('days', 30)),
            request.GET.get('platform', 'Amazon'),
        )
        return api_success(suggestion)
    except Exception as e:
        return api_error(str(e))
