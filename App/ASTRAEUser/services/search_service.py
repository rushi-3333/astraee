"""Intelligent category detection from unified search queries."""
import re

CATEGORY_KEYWORDS = {
    'ride': [
        'uber', 'ola', 'rapido', 'cab', 'taxi', 'auto', 'bike', 'from', 'to',
        'airport', 'station', 'ride', 'pickup', 'drop',
    ],
    'food': [
        'pizza', 'biryani', 'burger', 'restaurant', 'food', 'swiggy', 'zomato',
        'dinner', 'lunch', 'breakfast', 'near me', 'craving',
    ],
    'grocery': [
        'grocery', 'groceries', 'vegetable', 'fruits', 'bigbasket', 'zepto',
        'blinkit', 'milk', 'bread', 'under ₹', 'under rs',
    ],
    'medicine': [
        'medicine', 'pharmacy', 'tablet', 'syrup', 'dolo', 'cold', 'fever',
        'netmeds', 'pharmeasy', 'apollo', 'prescription', 'rx',
    ],
    'fashion': [
        'myntra', 'ajio', 'dress', 'shirt', 'shoes', 'fashion', 'clothing',
        'sneakers', 'kurta', 'jeans',
    ],
    'beauty': [
        'nykaa', 'beauty', 'makeup', 'skincare', 'lipstick', 'perfume',
    ],
    'shopping': [
        'amazon', 'flipkart', 'iphone', 'laptop', 'phone', 'electronics',
        'buy', 'product', 'shopping',
    ],
}


def detect_category(query: str) -> tuple:
    """
    Detect category and parse query into (category, q1, q2).
    Returns (category, location/from, item/destination).
    """
    q = query.strip().lower()
    if not q:
        return 'ride', 'Hyderabad', 'Hitech City'

    # Ride pattern: "X from Y to Z" or "Y to Z"
    ride_match = re.search(
        r'(?:from\s+)?(.+?)\s+(?:to|→)\s+(.+)',
        query, re.IGNORECASE
    )
    if ride_match:
        return 'ride', ride_match.group(1).strip(), ride_match.group(2).strip()

    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in q)

    best = max(scores, key=scores.get) if max(scores.values()) > 0 else 'shopping'

    # Grocery budget pattern
    budget_match = re.search(r'under\s+[₹rs.]?\s*(\d+)', q, re.IGNORECASE)
    if budget_match or 'grocer' in q:
        return 'grocery', 'Hyderabad', query.strip()

    if 'near me' in q or any(k in q for k in ['pizza', 'biryani', 'restaurant', 'food']):
        return 'food', 'Hyderabad', query.strip()

    if any(k in q for k in ['medicine', 'tablet', 'pharmacy', 'dolo', 'cold']):
        return 'medicine', 'Hyderabad', query.strip()

    return best, 'Hyderabad', query.strip()
