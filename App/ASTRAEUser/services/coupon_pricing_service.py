"""Dynamic coupon marketplace pricing — transparent formula."""

PLATFORM_POPULARITY = {
    'Amazon': 95, 'Flipkart': 90, 'Swiggy': 88, 'Zomato': 85,
    'Uber': 82, 'Myntra': 80, 'Ola': 78, 'Nykaa': 75,
    'BigBasket': 72, 'Zepto': 70, 'Blinkit': 68, 'Rapido': 65,
    'Netmeds': 60, 'PharmEasy': 58, 'Apollo Pharmacy': 55, 'Ajio': 70,
}


def suggest_coupon_price(
    face_value: float,
    discount_value: float,
    days_until_expiry: int,
    platform: str,
    category: str = '',
    seller_asking: int = None,
) -> dict:
    """
    Transparent pricing formula:
    base = face_value * 0.25 + discount_value * 0.15
    expiry_factor = max(0.5, days_until_expiry / 30)
    demand_factor = platform_popularity / 100
    suggested = base * expiry_factor * demand_factor
    """
    pop = PLATFORM_POPULARITY.get(platform, 50) / 100.0
    expiry_factor = max(0.3, min(1.0, days_until_expiry / 30.0))
    base = face_value * 0.25 + discount_value * 0.15
    suggested = int(round(base * expiry_factor * pop))
    suggested = max(10, min(suggested, int(face_value * 0.5)))

    low = max(10, int(suggested * 0.85))
    high = int(suggested * 1.15)

    return {
        'suggested_price': suggested,
        'price_range': {'min': low, 'max': high},
        'factors': {
            'face_value': face_value,
            'discount_value': discount_value,
            'days_until_expiry': days_until_expiry,
            'platform_popularity': pop,
            'expiry_factor': round(expiry_factor, 2),
        },
        'formula': 'base = face_value×0.25 + discount×0.15; price = base × expiry_factor × popularity',
    }
