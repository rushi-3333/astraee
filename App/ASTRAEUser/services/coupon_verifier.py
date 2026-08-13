"""Coupon verification architecture — demo mode with provider interface."""
import re
from datetime import date
from abc import ABC, abstractmethod
from django.utils import timezone
from ASTRAEUser.models import UserCoupon


class CouponVerifier(ABC):
    @abstractmethod
    def verify(self, platform: str, coupon_code: str, expiry_date=None) -> dict:
        pass


class DemoCouponVerifier(CouponVerifier):
    """Demo verification — format, expiry, duplicate checks only."""

    PLATFORM_PATTERNS = {
        'Uber': r'^UBR[A-Z0-9]{4,12}$',
        'Ola': r'^OLA[A-Z0-9]{4,12}$',
        'Swiggy': r'^SWG[A-Z0-9]{4,12}$',
        'Zomato': r'^ZMT[A-Z0-9]{4,12}$',
        'Amazon': r'^AMZ[A-Z0-9]{4,12}$',
        'Flipkart': r'^FLK[A-Z0-9]{4,12}$',
        'Myntra': r'^MYN[A-Z0-9]{4,12}$',
        'BigBasket': r'^BBK[A-Z0-9]{4,12}$',
        'Zepto': r'^ZPT[A-Z0-9]{4,12}$',
        'Blinkit': r'^BLK[A-Z0-9]{4,12}$',
        'Nykaa': r'^NYK[A-Z0-9]{4,12}$',
        'Netmeds': r'^NTM[A-Z0-9]{4,12}$',
        'PharmEasy': r'^PHE[A-Z0-9]{4,12}$',
        'Apollo Pharmacy': r'^APL[A-Z0-9]{4,12}$',
        'Rapido': r'^RPD[A-Z0-9]{4,12}$',
        'Ajio': r'^AJO[A-Z0-9]{4,12}$',
    }

    GENERIC_PATTERN = r'^[A-Z0-9]{4,20}$'

    def verify(self, platform: str, coupon_code: str, expiry_date=None) -> dict:
        code = coupon_code.strip().upper()
        errors = []

        pattern = self.PLATFORM_PATTERNS.get(platform, self.GENERIC_PATTERN)
        if not re.match(pattern, code, re.IGNORECASE):
            # Allow DEMO prefix codes
            if not code.startswith('DEMO'):
                errors.append(f'Invalid coupon format for {platform}')

        if UserCoupon.objects.filter(coupon_code__iexact=code, platform=platform).exists():
            errors.append('This coupon code is already registered on ASTRAE')

        if expiry_date and expiry_date < date.today():
            errors.append('Coupon has expired')

        if errors:
            return {'valid': False, 'status': 'rejected', 'errors': errors}

        return {
            'valid': True,
            'status': 'verified',
            'errors': [],
            'message': 'Demo verification passed (format & duplicate check only)',
        }


def verify_and_update_coupon(coupon: UserCoupon) -> dict:
    verifier = DemoCouponVerifier()
    result = verifier.verify(coupon.platform, coupon.coupon_code, coupon.expiry_date)
    coupon.status = result['status']
    coupon.save(update_fields=['status'])
    return result
