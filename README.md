# ASTRAE — Unified Multi-Service Comparison and Rewards Marketplace

> **One Search. Every Better Choice.**

ASTRAE is a Django-based unified discovery and comparison platform that lets users search once and compare prices, offers, rewards, and services across multiple platforms — rides, food, grocery, e-commerce, fashion, beauty, and medicine.

Built as a final-year major project with a production-style architecture, transparent scoring, and a full demo ecosystem.

![ASTRAE](App/static/img/logo.svg)

---

## Features

| Module | Description |
|--------|-------------|
| **Unified Search** | One search bar with intelligent category detection |
| **Platform Comparison** | Side-by-side results from Uber, Ola, Swiggy, Amazon, and 16+ demo providers |
| **ASTRAE Score** | Transparent multi-factor scoring (price, rating, cashback, delivery, coupons) |
| **Deals Hub** | Filterable deals with deal scores |
| **Coupon Marketplace** | Buy & sell coupons with reward points |
| **Rewards Wallet** | Configurable reward rules and point history |
| **Savings Dashboard** | Charts for spending, savings, and category breakdown |
| **Orders** | Full order lifecycle with timeline |
| **Wishlist & Price Alerts** | Save items and set target prices |
| **Notifications** | Price drops, coupons, rewards, orders |
| **Admin Dashboard** | User activation, analytics, marketplace logs |

---

## Tech Stack

- **Backend:** Django 6.1, SQLite (development)
- **Frontend:** Tailwind CSS, Plus Jakarta Sans, custom ASTRAE design system
- **ML (optional):** CatBoost, scikit-learn, ChromaDB, Sentence Transformers
- **Demo mode:** Mock providers with deterministic pricing (no live third-party APIs)

---

## Quick Start

### Prerequisites

- Python 3.12+
- pip

### Installation

```powershell
cd App

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Migrate database
python manage.py migrate

# Seed demo data (platforms, deals, coupons)
python manage.py seed_demo_data

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### URLs

| Page | URL |
|------|-----|
| Landing | http://127.0.0.1:8000/ |
| User Home | http://127.0.0.1:8000/ASTRAEUser/userhome/ |
| Compare | http://127.0.0.1:8000/ASTRAEUser/usersearch/ |
| Deals | http://127.0.0.1:8000/ASTRAEUser/userdeals/ |
| Coupons | http://127.0.0.1:8000/ASTRAEUser/usercoupons/ |
| Rewards | http://127.0.0.1:8000/ASTRAEUser/userrewards/ |
| Admin | http://127.0.0.1:8000/ASTRAEAdmin/adminhome/ |

---

## User Flow

```
SEARCH → COMPARE → FIND BEST VALUE → BOOK → EARN REWARDS → COUPON MARKETPLACE → SAVE MORE
```

### First-time setup

1. **Register** at `/register/` — account starts inactive
2. **Admin activates** user at `/ASTRAEAdmin/adminhome/` or `/admin/`
3. **Log in** and search e.g. `Uber from Hitech City to Gachibowli`
4. **Compare** results, book the ASTRAE Recommended option
5. **Earn** reward points and coupons
6. **Trade** coupons on the marketplace

---

## Management Commands

```powershell
python manage.py seed_platforms      # Categories & platforms
python manage.py seed_deals          # Demo deals
python manage.py seed_coupons        # Demo marketplace coupons
python manage.py seed_demo_data      # All of the above
python manage.py check_price_alerts  # Simulate price-drop notifications
```

---

## Project Structure

```
App/
├── ASTRAE/              # Django settings & root URLs
├── ASTRAEUser/          # Main app (models, views, services)
│   ├── services/        # Search, scoring, coupons, rewards
│   ├── management/      # Seed commands
│   └── migrations/
├── ASTRAEAdmin/         # Staff dashboard
├── Templates/           # HTML templates
├── static/              # CSS, JS, logo, favicon
│   ├── css/astrae.css
│   ├── js/astrae.js
│   └── img/
├── Model/               # ML models & datasets (optional)
└── manage.py
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ASTRAEUser/api/search/` | GET | Unified search JSON |
| `/ASTRAEUser/api/deals/` | GET | Deals list JSON |
| `/ASTRAEUser/api/coupon-price/` | GET | Coupon price suggestion |

---

## Design System

- **Colors:** Deep navy `#0B1220`, Indigo `#4F46E5`, Cyan `#06B6D4`, Light bg `#F8FAFC`
- **Font:** Plus Jakarta Sans
- **Components:** Cards, badges, comparison table, timeline, tabs, empty states

---

## Demo Mode Disclaimer

ASTRAE uses **simulated provider data** for development and academic presentation. Coupon codes are marked `DEMO-*` and `is_demo=True`. No real third-party API transactions occur unless explicitly integrated in the future.

---

## License

Academic / educational project — © 2026 ASTRAE Team.
