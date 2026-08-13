"""
Provider abstraction layer for ASTRAE.
Each provider returns normalized comparison results.
Replace mock implementations with real API integrations later.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class NormalizedResult:
    platform: str
    item_title: str
    category: str
    original_price: float
    discount: float = 0.0
    coupon: str = ''
    cashback: float = 0.0
    delivery_fee: float = 0.0
    estimated_delivery: str = ''
    rating: float = 4.0
    availability: str = 'Available'
    final_price: float = 0.0
    savings: float = 0.0
    provider_url: str = '#'
    provider_logo: str = ''
    eta_mins: int = 30
    badge: str = ''
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        d = asdict(self)
        d['coupon_discount'] = self.discount
        d['delivery_info'] = self.estimated_delivery
        return d


class BaseProvider(ABC):
    platform_name: str = ''
    category: str = ''
    integration_type: str = 'mock'

    @abstractmethod
    def search(self, query1: str, query2: str, limit: int = 5) -> List[NormalizedResult]:
        pass

    def is_available(self) -> bool:
        return True

    def unavailable_message(self) -> str:
        return f"{self.platform_name} data is temporarily unavailable."
