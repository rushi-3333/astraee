"""ASTRAE Smart Score — transparent multi-factor scoring algorithm."""

WEIGHTS = {
    'price': 0.30,
    'discount': 0.15,
    'cashback': 0.10,
    'rating': 0.20,
    'delivery': 0.15,
    'coupon': 0.10,
}


def _normalize(value, min_v, max_v, invert=False):
    if max_v == min_v:
        return 100.0
    score = 100.0 * (value - min_v) / (max_v - min_v)
    if invert:
        score = 100.0 - score
    return max(0.0, min(100.0, score))


def compute_astrae_scores(candidates: list) -> list:
    """Add astrae_score and score_reasons to each candidate."""
    if not candidates:
        return []

    prices = [c.get('final_price', 0) for c in candidates]
    discounts = [c.get('discount', c.get('coupon_discount', 0)) for c in candidates]
    cashbacks = [c.get('cashback', 0) for c in candidates]
    ratings = [c.get('rating', 4.0) for c in candidates]
    etas = [c.get('eta_mins', 30) for c in candidates]

    min_p, max_p = min(prices), max(prices)
    min_d, max_d = min(discounts), max(discounts)
    min_cb, max_cb = min(cashbacks), max(cashbacks)
    min_r, max_r = min(ratings), max(ratings)
    min_e, max_e = min(etas), max(etas)
    avg_price = sum(prices) / len(prices)

    scored = []
    for c in candidates:
        price_score = _normalize(c.get('final_price', 0), min_p, max_p, invert=True)
        discount_score = _normalize(c.get('discount', c.get('coupon_discount', 0)), min_d, max_d)
        cashback_score = _normalize(c.get('cashback', 0), min_cb, max_cb)
        rating_score = _normalize(c.get('rating', 4.0), min_r, max_r)
        delivery_score = _normalize(c.get('eta_mins', 30), min_e, max_e, invert=True)
        coupon_score = 100.0 if c.get('coupon') or c.get('coupon_discount', 0) > 0 else 30.0

        total = (
            price_score * WEIGHTS['price']
            + discount_score * WEIGHTS['discount']
            + cashback_score * WEIGHTS['cashback']
            + rating_score * WEIGHTS['rating']
            + delivery_score * WEIGHTS['delivery']
            + coupon_score * WEIGHTS['coupon']
        )
        astrae_score = int(round(total))

        reasons = []
        fp = c.get('final_price', 0)
        if fp <= min_p:
            reasons.append('Lowest price among compared options')
        elif fp < avg_price:
            savings_vs_avg = round(avg_price - fp, 2)
            reasons.append(f'₹{savings_vs_avg} cheaper than the average option')
        if c.get('eta_mins', 999) <= min_e:
            reasons.append('Fastest estimated delivery/pickup')
        if c.get('rating', 0) >= max_r:
            reasons.append('Highest rated option')
        if c.get('cashback', 0) > 0:
            reasons.append(f'₹{c["cashback"]} cashback available')
        if c.get('discount', c.get('coupon_discount', 0)) > 0:
            reasons.append(f'₹{c.get("discount", c.get("coupon_discount", 0))} discount applied')
        if c.get('coupon') or c.get('coupon_code'):
            reasons.append('Coupon available on this option')
        if c.get('astrae_score', 0) >= 85:
            reasons.append('Top ASTRAE Score in this comparison')

        copy = dict(c)
        copy['astrae_score'] = astrae_score
        copy['score_breakdown'] = {
            'price': int(price_score),
            'discount': int(discount_score),
            'cashback': int(cashback_score),
            'rating': int(rating_score),
            'delivery': int(delivery_score),
            'coupon': int(coupon_score),
        }
        copy['score_reasons'] = reasons[:4] or ['Balanced value across all factors']
        scored.append(copy)

    return sorted(scored, key=lambda x: x['astrae_score'], reverse=True)


def get_comparison_highlights(candidates: list) -> dict:
    """Return best_price, fastest, best_rated, best_overall labels."""
    if not candidates:
        return {}
    by_price = min(candidates, key=lambda x: x.get('final_price', 999999))
    by_eta = min(candidates, key=lambda x: x.get('eta_mins', 999999))
    by_rating = max(candidates, key=lambda x: x.get('rating', 0))
    by_score = max(candidates, key=lambda x: x.get('astrae_score', 0))
    return {
        'best_price': by_price.get('platform'),
        'fastest': by_eta.get('platform'),
        'best_rated': by_rating.get('platform'),
        'best_overall': by_score.get('platform'),
        'recommended': by_score,
    }
