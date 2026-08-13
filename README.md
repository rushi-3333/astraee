# ASTRAE — Unified Multi-Service Comparison and Rewards Marketplace

> **One Search. Every Better Choice.**

ASTRAE is a Django-based unified discovery and comparison platform that lets users search once and compare prices, offers, rewards, and services across multiple platforms — rides, food, grocery, e-commerce, fashion, beauty, and medicine.

Built as a final-year major project with a production-style architecture, transparent scoring, a full demo ecosystem, and a cohesive end-to-end user journey.

![ASTRAE](App/static/img/logo.svg)

---

## Features Overview

| Module | Description |
|--------|-------------|
| **Unified Search** | One search bar with intelligent category detection |
| **Platform Comparison** | Side-by-side results with ASTRAE Score + AIRE ranking |
| **Why ASTRAE Recommends** | Transparent reasons (price, rating, delivery, coupon, cashback) |
| **Events & Offers** | Upcoming, live, flash sales, festival & platform-specific offers |
| **Deals Hub** | Filterable deals with deal scores and ending-soon sort |
| **Booking Flow** | Date, time slot, address & quantity before order confirmation |
| **Coupon Marketplace** | Atomic buy/sell with verification, expiry & duplicate protection |
| **Rewards Wallet** | Available, lifetime, used & pending points with configurable rules |
| **My Savings** | Real savings from orders — comparison, coupons, cashback, rewards |
| **Watchlist** | Save products/services with price tracking & alert creation |
| **Price & Offer Alerts** | Price drops, coupon expiry, deal expiry, events (demo notifications) |
| **Notifications** | In-app alerts for orders, rewards, marketplace, price drops |
| **Personalized Home** | "Picked for you" or honest "Trending on ASTRAE" |
| **Admin Dashboard** | Users, searches, orders, savings, platform health & charts |

---

## Supported Platforms (Demo)

| Category | Platforms |
|----------|-----------|
| **Rides** | Uber, Ola, Rapido |
| **Food** | Swiggy, Zomato |
| **Grocery** | BigBasket, Zepto, Blinkit |
| **Shopping** | Amazon, Flipkart |
| **Fashion** | Myntra, Ajio |
| **Beauty** | Nykaa |
| **Medicine** | Netmeds, PharmEasy, Apollo Pharmacy |

All platform data is **mock/demo** unless a real API integration is added. Demo offers and coupons are clearly labeled.

---

## Complete User Flow

```
SEARCH
  ↓
COMPARE PLATFORMS
  ↓
ASTRAE RECOMMENDATION (with reasons)
  ↓
BOOK / SELECT DATE & TIME
  ↓
SAVE MONEY
  ↓
EARN REWARDS
  ↓
RECEIVE COUPON
  ↓
USE / SELL COUPON (marketplace)
  ↓
TRACK SAVINGS
  ↓
WATCH PRICES (watchlist + alerts)
  ↓
DISCOVER EVENTS & OFFERS
  ↓
SAVE MORE
```

---

## Navigation

### Desktop (top navbar)
Home · Compare · Deals · **Events** · Coupons · Rewards

### Mobile (bottom bar — 5 tabs)
Home · Search · Deals · Rewards · Profile

### Profile menu
Orders · Watchlist · My Savings · My Coupons · Events & Offers · Rewards · Price Alerts · Notifications · Settings

---

## Tech Stack

- **Backend:** Django 6.1, SQLite (development)
- **Frontend:** Tailwind CSS (CDN), Plus Jakarta Sans, ASTRAE design system (`astrae.css`, `astrae.js`)
- **ML (optional):** CatBoost, scikit-learn, ChromaDB, Sentence Transformers, AIRE RL ranking
- **Charts:** Chart.js (savings dashboard, admin analytics)
- **Demo mode:** Mock providers with deterministic pricing — no live third-party APIs

---

## Quick Start

### Prerequisites

- Python 3.12+
- pip

### Installation

```powershell
cd App

# Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Seed demo data (platforms, deals, coupons, events, reward rules)
python manage.py seed_demo_data

# Optional: seed events separately
python manage.py seed_events

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### First-time user setup

1. **Register** at `/register/` — account starts inactive (admin approval)
2. **Admin activates** user at `/ASTRAEAdmin/adminhome/` or Django `/admin/`
3. **Log in** and search e.g. `Uber from Hitech City to Gachibowli` or `iPhone 16`
4. **Compare** results — read **Why ASTRAE recommends this**
5. **Book** with date, time slot & delivery details
6. **Earn** reward points and demo coupons
7. **Track** savings, watchlist items, and set price alerts
8. **Browse** Events & Offers and the coupon marketplace

---

## Page URLs

| Page | URL |
|------|-----|
| Landing | http://127.0.0.1:8000/ |
| User Home | http://127.0.0.1:8000/ASTRAEUser/userhome/ |
| Compare / Search | http://127.0.0.1:8000/ASTRAEUser/usersearch/ |
| Deals | http://127.0.0.1:8000/ASTRAEUser/userdeals/ |
| **Events & Offers** | http://127.0.0.1:8000/ASTRAEUser/userevents/ |
| Event Detail | http://127.0.0.1:8000/ASTRAEUser/events/\<id\>/ |
| Book Offer | http://127.0.0.1:8000/ASTRAEUser/book/ |
| Coupons | http://127.0.0.1:8000/ASTRAEUser/usercoupons/ |
| Rewards | http://127.0.0.1:8000/ASTRAEUser/userrewards/ |
| **My Savings** | http://127.0.0.1:8000/ASTRAEUser/usersavings/ |
| **Watchlist** | http://127.0.0.1:8000/ASTRAEUser/userwishlist/ |
| **Price Alerts** | http://127.0.0.1:8000/ASTRAEUser/useralerts/ |
| Orders | http://127.0.0.1:8000/ASTRAEUser/userorders/ |
| Notifications | http://127.0.0.1:8000/ASTRAEUser/usernotifications/ |
| Profile | http://127.0.0.1:8000/ASTRAEUser/userprofile/ |
| Admin Dashboard | http://127.0.0.1:8000/ASTRAEAdmin/adminhome/ |
| Django Admin | http://127.0.0.1:8000/admin/ |

---

## Feature Details

### Events & Offers
- Filter by platform, category, **Upcoming**, **Live Now**, **Ending Soon**
- Event types: Festival Sale, Flash Sale, Live Offer, Platform Offer
- Each card: platform, dates, benefit, description, **View Offer** → detail → book with time slots
- Sample data only — marked **Demo**

### Compare & ASTRAE Recommendation
- ASTRAE Score (price, discount, cashback, rating, delivery, coupon)
- AIRE ML ranking blended when models are available
- **Why ASTRAE recommends this** — human-readable reasons from real comparison data

### Booking
- No instant order placement — users select **date**, **time slot**, address/location, quantity
- Orders saved as **Confirmed** with schedule; reschedule from Orders page

### Watchlist & Alerts
- Save products from compare results
- Set target price alerts from watchlist
- Alert types: price drop, coupon expiry, deal expiry, new offer, event starting
- Run `python manage.py check_price_alerts` to simulate demo notifications

### My Savings
- Total saved from actual `astrae_savings` on orders (no fake claims when data exists)
- Breakdown: comparison, coupons, cashback, rewards, marketplace earnings
- Monthly charts and category breakdown (Chart.js)

### Rewards
- **Available**, **Lifetime**, **Used**, **Pending** points
- Configurable rules via `RewardRule` model (order, coupon sold, daily login, referral)
- Wallet transactions and reward history

### Coupon Marketplace
- Status flow: verified → listed → sold (with demo verification)
- **Verified Coupon** badge, **Expires in X days**
- Atomic purchase: balance check, ownership transfer, rollback on failure
- Blocks: own coupon, duplicate listing, expired, insufficient points

### Admin Dashboard
- Metrics: users, active users, searches, orders, coupons, sales, rewards, total savings
- Charts: orders by category, top platforms
- **Platform Health:** Active / Demo / Unavailable per provider
- User activation toggle

---

## Management Commands

```powershell
python manage.py seed_platforms       # Categories & 16+ platforms
python manage.py seed_deals           # Demo deals
python manage.py seed_coupons         # Demo marketplace coupons
python manage.py seed_events          # Demo events & offers
python manage.py seed_demo_data       # All seeds above (recommended)
python manage.py check_price_alerts   # Simulate price-drop & offer alerts
python manage.py check                # Django system check
```

---

## Project Structure

```
App/
├── ASTRAE/                 # Django settings & root URLs
├── ASTRAEUser/             # Main app (models, views, services)
│   ├── models.py           # Order, Deal, PlatformEvent, PriceAlert, Wishlist, etc.
│   ├── views.py            # All user-facing views
│   ├── services/
│   │   ├── unified_search_service.py
│   │   ├── astrae_score_service.py
│   │   ├── recommendation_service.py   # AIRE ranking
│   │   ├── deals_service.py
│   │   ├── events_service.py
│   │   ├── booking_service.py
│   │   ├── order_service.py
│   │   ├── coupon_marketplace_service.py  # Atomic coupon buy
│   │   ├── coupon_verifier.py
│   │   ├── reward_service.py
│   │   ├── savings_service.py
│   │   ├── personalization_service.py
│   │   ├── alert_service.py
│   │   └── admin_analytics_service.py
│   ├── management/commands/
│   └── migrations/
├── ASTRAEAdmin/            # Staff analytics dashboard
├── Templates/
│   ├── User/               # userhome, usersearch, userevents, userbook, etc.
│   ├── Admin/
│   └── includes/           # logo, time_slot_picker, astrae_head
├── static/
│   ├── css/astrae.css      # Design system
│   ├── js/astrae.js
│   └── img/                # Logo & favicon
├── Model/                  # ML models & ChromaDB (optional)
└── manage.py
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ASTRAEUser/api/search/` | GET | Unified search JSON |
| `/ASTRAEUser/api/deals/` | GET | Deals list JSON |
| `/ASTRAEUser/api/coupon-price/` | GET | Coupon marketplace price suggestion |

---

## Design System

- **Colors:** Navy `#0B1220`, Indigo `#4F46E5`, Cyan `#06B6D4`, Background `#F8FAFC`
- **Font:** Plus Jakarta Sans
- **Components:** Cards, badges, comparison table, timeline, tabs, time-slot picker, empty states, hero gradient
- **Responsive:** Desktop navbar + mobile bottom navigation

---

## Git — Push Changes (VS Code)

Open the integrated terminal in VS Code:

```powershell
cd "E:\Projects\Major Project\Astrae Unified Multi-Service Comparison and Rewards Marketplace"

git status
git add .
git commit -m "Your commit message here"
git push origin main
```

Or use **Source Control** panel: Stage → Commit → **Sync Changes**.

Pull latest before pushing:

```powershell
git pull origin main
git push origin main
```

**Repository:** https://github.com/rushi-3333/astraee.git

---

## Demo Mode Disclaimer

ASTRAE uses **simulated provider data** for development and academic presentation.

- Coupons are marked `DEMO-*` and `is_demo=True`
- Events & offers are sample data — not live external promotions
- Price alerts use deterministic demo price simulation
- No real third-party API transactions occur unless explicitly integrated

The app does **not** claim offers, prices, or events are live unless connected to a real data source.

---

## License

Academic / educational project — © 2026 ASTRAE Team.
