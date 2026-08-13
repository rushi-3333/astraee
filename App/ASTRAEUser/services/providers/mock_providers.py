"""
Mock provider implementations for demo/development.
Data is deterministic based on query hash — not random per request.
"""
import hashlib
from typing import List
from .base import BaseProvider, NormalizedResult


def _seeded_value(text: str, lo: float, hi: float) -> float:
    h = int(hashlib.md5(text.encode()).hexdigest(), 16)
    return lo + (h % 1000) / 1000.0 * (hi - lo)


def _seeded_int(text: str, lo: int, hi: int) -> int:
    return int(_seeded_value(text, lo, hi))


class MockRideProvider(BaseProvider):
    def __init__(self, platform: str):
        self.platform_name = platform
        self.category = 'ride'

    def search(self, query1: str, query2: str, limit: int = 5) -> List[NormalizedResult]:
        key = f"{self.platform_name}:{query1}:{query2}"
        base = _seeded_value(key, 80, 200)
        surge = 1.0 + _seeded_value(key + 'surge', 0, 0.4)
        original = round(base * surge, 2)
        discount = round(_seeded_value(key + 'disc', 5, 25), 2)
        final = round(original - discount, 2)
        eta = _seeded_int(key + 'eta', 3, 12)
        rating = round(_seeded_value(key + 'rat', 3.8, 4.9), 1)
        cashback = round(_seeded_value(key + 'cb', 3, 15), 2)
        return [NormalizedResult(
            platform=self.platform_name,
            item_title=f"{query1} → {query2}",
            category='ride',
            original_price=original,
            discount=discount,
            coupon=f"{self.platform_name[:3].upper()}RIDE{int(discount)}",
            cashback=cashback,
            delivery_fee=0,
            estimated_delivery=f"{eta} min ETA",
            rating=rating,
            availability='Available',
            final_price=final,
            savings=round(original - final + cashback, 2),
            provider_url='#',
            eta_mins=eta,
            badge='Surge Applied' if surge > 1.2 else 'Best Offer',
        )]


class MockFoodProvider(BaseProvider):
    def __init__(self, platform: str):
        self.platform_name = platform
        self.category = 'food'

    def search(self, query1: str, query2: str, limit: int = 5) -> List[NormalizedResult]:
        key = f"{self.platform_name}:{query1}:{query2}"
        original = round(_seeded_value(key, 150, 600), 2)
        discount = round(_seeded_value(key + 'disc', 20, 80), 2)
        delivery = round(_seeded_value(key + 'del', 0, 40), 2)
        final = round(original - discount + delivery, 2)
        eta = _seeded_int(key + 'eta', 20, 50)
        rating = round(_seeded_value(key + 'rat', 3.5, 4.8), 1)
        cashback = round(_seeded_value(key + 'cb', 5, 30), 2)
        return [NormalizedResult(
            platform=self.platform_name,
            item_title=query2 or 'Popular Item',
            category='food',
            original_price=original,
            discount=discount,
            coupon=f"{self.platform_name[:3].upper()}FOOD{int(discount)}",
            cashback=cashback,
            delivery_fee=delivery,
            estimated_delivery=f"{eta} mins",
            rating=rating,
            availability='Available',
            final_price=final,
            savings=round(original - final + cashback, 2),
            provider_url='#',
            eta_mins=eta,
            badge='Free Delivery' if delivery == 0 else 'Popular',
        )]


class MockGroceryProvider(BaseProvider):
    def __init__(self, platform: str):
        self.platform_name = platform
        self.category = 'grocery'

    def search(self, query1: str, query2: str, limit: int = 5) -> List[NormalizedResult]:
        key = f"{self.platform_name}:{query1}:{query2}"
        original = round(_seeded_value(key, 200, 1500), 2)
        discount = round(_seeded_value(key + 'disc', 30, 150), 2)
        delivery = round(_seeded_value(key + 'del', 0, 30), 2)
        final = round(original - discount + delivery, 2)
        eta = _seeded_int(key + 'eta', 10, 45)
        rating = round(_seeded_value(key + 'rat', 3.8, 4.7), 1)
        cashback = round(_seeded_value(key + 'cb', 10, 50), 2)
        return [NormalizedResult(
            platform=self.platform_name,
            item_title=query2 or 'Grocery Basket',
            category='grocery',
            original_price=original,
            discount=discount,
            coupon=f"{self.platform_name[:3].upper()}GROC{int(discount)}",
            cashback=cashback,
            delivery_fee=delivery,
            estimated_delivery=f"{eta} mins",
            rating=rating,
            availability='In Stock',
            final_price=final,
            savings=round(original - final + cashback, 2),
            provider_url='#',
            eta_mins=eta,
            badge='Express Delivery' if eta <= 15 else 'Best Value',
        )]


class MockShoppingProvider(BaseProvider):
    def __init__(self, platform: str):
        self.platform_name = platform
        self.category = 'shopping'

    def search(self, query1: str, query2: str, limit: int = 5) -> List[NormalizedResult]:
        key = f"{self.platform_name}:{query1}:{query2}"
        original = round(_seeded_value(key, 500, 80000), 2)
        discount = round(_seeded_value(key + 'disc', 50, 5000), 2)
        final = round(original - discount, 2)
        days = _seeded_int(key + 'days', 1, 7)
        rating = round(_seeded_value(key + 'rat', 3.5, 4.9), 1)
        cashback = round(_seeded_value(key + 'cb', 20, 500), 2)
        return [NormalizedResult(
            platform=self.platform_name,
            item_title=query2 or 'Product',
            category='shopping',
            original_price=original,
            discount=discount,
            coupon=f"{self.platform_name[:3].upper()}SHOP{int(discount % 1000)}",
            cashback=cashback,
            delivery_fee=0,
            estimated_delivery=f"{days} days",
            rating=rating,
            availability='In Stock',
            final_price=final,
            savings=round(original - final + cashback, 2),
            provider_url='#',
            eta_mins=days * 1440,
            badge='Cheapest' if discount / max(original, 1) > 0.15 else 'Best Value',
        )]


class MockMedicineProvider(BaseProvider):
    def __init__(self, platform: str):
        self.platform_name = platform
        self.category = 'medicine'

    def search(self, query1: str, query2: str, limit: int = 5) -> List[NormalizedResult]:
        key = f"{self.platform_name}:{query1}:{query2}"
        original = round(_seeded_value(key, 50, 800), 2)
        discount = round(_seeded_value(key + 'disc', 5, 80), 2)
        final = round(original - discount, 2)
        hours = _seeded_int(key + 'hrs', 2, 48)
        rating = round(_seeded_value(key + 'rat', 4.0, 4.9), 1)
        cashback = round(_seeded_value(key + 'cb', 2, 20), 2)
        return [NormalizedResult(
            platform=self.platform_name,
            item_title=query2 or 'Medicine',
            category='medicine',
            original_price=original,
            discount=discount,
            coupon=f"{self.platform_name[:3].upper()}MED{int(discount)}",
            cashback=cashback,
            delivery_fee=0,
            estimated_delivery=f"{hours} hrs",
            rating=rating,
            availability='In Stock',
            final_price=final,
            savings=round(original - final + cashback, 2),
            provider_url='#',
            eta_mins=hours * 60,
            badge='Rx Required' if 'prescription' in query2.lower() else 'In Stock',
        )]
