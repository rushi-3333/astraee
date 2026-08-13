"""ASTRAE Wallet — server-side balance management."""
from decimal import Decimal
from django.db import transaction
from django.contrib.auth.models import User
from ASTRAEUser.models import Wallet, WalletTransaction, Reward


def get_or_create_wallet(user: User) -> Wallet:
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


def sync_wallet_from_rewards(user: User) -> Wallet:
    """Sync reward_points from Reward ledger (source of truth for points)."""
    wallet = get_or_create_wallet(user)
    total = Reward.objects.filter(user=user).aggregate(
        total=__import__('django.db.models', fromlist=['Sum']).Sum('points_earned')
    )['total'] or 0
    wallet.reward_points = total
    wallet.save(update_fields=['reward_points', 'updated_at'])
    return wallet


@transaction.atomic
def credit_points(user: User, points: int, description: str, txn_type: str = 'earned', reference_id: str = ''):
    wallet = sync_wallet_from_rewards(user)
    WalletTransaction.objects.create(
        wallet=wallet,
        txn_type=txn_type,
        points_delta=points,
        description=description,
        reference_id=reference_id,
    )
    return wallet


@transaction.atomic
def debit_points(user: User, points: int, description: str, txn_type: str = 'spent', reference_id: str = '') -> bool:
    wallet = sync_wallet_from_rewards(user)
    if wallet.reward_points < points:
        return False
    WalletTransaction.objects.create(
        wallet=wallet,
        txn_type=txn_type,
        points_delta=-points,
        description=description,
        reference_id=reference_id,
    )
    sync_wallet_from_rewards(user)
    return True


def get_wallet_summary(user: User) -> dict:
    wallet = sync_wallet_from_rewards(user)
    txns = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:20]
    earned = sum(t.points_delta for t in txns if t.points_delta > 0)
    spent = abs(sum(t.points_delta for t in txns if t.points_delta < 0))
    return {
        'reward_points': wallet.reward_points,
        'cashback_balance': float(wallet.cashback_balance),
        'coupon_credits': wallet.coupon_credits,
        'marketplace_earnings': wallet.marketplace_earnings,
        'recent_earned': earned,
        'recent_spent': spent,
        'transactions': txns,
    }
