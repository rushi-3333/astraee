# ASTRAE — Unified Multi-Service Comparison and Rewards Marketplace

> **One Search. Every Better Choice.**

ASTRAE is a Django web application that lets users **search once**, **compare prices and offers** across multiple platforms (rides, food, grocery, shopping, fashion, beauty, medicine), **book** the best option, **earn rewards**, **use or trade coupons**, and **track savings**.

Built as a final-year major project with a production-style architecture, transparent ASTRAE Score recommendations, and a full demo ecosystem for academic presentation.

![ASTRAE](App/static/img/logo.svg)

**Repository:** [github.com/rushi-3333/astraee](https://github.com/rushi-3333/astraee.git)

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Run the Application](#run-the-application)
- [Demo Login](#demo-login)
- [Quick Demo Walkthrough](#quick-demo-walkthrough)
- [Page URLs](#page-urls)
- [Features Overview](#features-overview)
- [Management Commands](#management-commands)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Troubleshooting](#troubleshooting)
- [Demo Mode Disclaimer](#demo-mode-disclaimer)

---

## Requirements

Install these **before** setting up the project.

| Requirement | Version | Notes |
|-------------|---------|--------|
| **Python** | 3.12 or higher | [python.org/downloads](https://www.python.org/downloads/) |
| **pip** | Latest | Bundled with Python; upgrade with `python -m pip install --upgrade pip` |
| **Git** | Any recent | To clone the repository |
| **Web browser** | Chrome, Firefox, Edge, or Safari | For using the app |

**Operating system:** Windows 10/11, macOS, or Linux.

**Optional (recommended):** A virtual environment (`venv`) to isolate dependencies.

### Python packages (installed via `requirements.txt`)

**Required** — app runs with these:

| Package | Purpose |
|---------|---------|
| Django 6.1 | Web framework |
| pandas | Data handling for ML & seeds |
| numpy | Numerical operations |
| scikit-learn | ML preprocessing |
| catboost | Price prediction models |
| joblib | Model serialization |

**Optional** — ML search uses mock data if these are not installed:

| Package | Purpose |
|---------|---------|
| chromadb | Vector search |
| sentence-transformers | Semantic embeddings |

> The app **works fully in demo mode** without ChromaDB or Sentence Transformers. Search uses mock providers with deterministic pricing.

---

## Installation

### Step 1 — Clone the repository

```powershell
git clone https://github.com/rushi-3333/astraee.git
cd astraee
```

If you already have the project folder, open a terminal in the project root.

### Step 2 — Go to the Django app folder

```powershell
cd App
```

All commands below are run from the **`App`** directory.

### Step 3 — Create and activate a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 4 — Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This installs Django and all required packages listed above.

### Step 5 — Set up the database

```powershell
python manage.py migrate
```

### Step 6 — Load demo data (recommended)

```powershell
python manage.py seed_demo_data
```

This creates:

- Platforms, categories, deals, coupons, and events  
- Reward rules  
- **Demo user:** `demo` / `demo123`  
- Sample coupons on the demo account for booking tests  

### Step 7 — Create an admin account (optional)

For the admin dashboard at `/ASTRAEAdmin/adminhome/`:

```powershell
python manage.py createsuperuser
```

Follow the prompts for username, email, and password.

### Step 8 — Verify installation

```powershell
python manage.py check
```

Expected output: `System check identified no issues (0 silenced).`

---

## Run the Application

From the **`App`** folder (with virtual environment activated):

```powershell
python manage.py runserver
```

Open in your browser:

**http://127.0.0.1:8000/**

To stop the server, press `Ctrl + C` in the terminal.

### Run on a different port

```powershell
python manage.py runserver 8080
```

Then open **http://127.0.0.1:8080/**

---

## Demo Login

After running `seed_demo_data`, use this account for instant access (no admin approval needed):

| Field | Value |
|-------|--------|
| **Username** | `demo` |
| **Password** | `demo123` |

**Login URL:** http://127.0.0.1:8000/loginn/

New registrations are **auto-activated** in demo mode (`ASTRAE_DEMO_MODE = True`).

---

## Quick Demo Walkthrough

1. **Log in** as `demo` / `demo123`
2. **Search** — e.g. `Uber from Hitech City to Gachibowli` or `iPhone 16`
3. **Compare** platforms and read **Why ASTRAE recommends this**
4. **Book** — pick date, time slot, address; optionally **apply a coupon**
5. **Orders** — view booking, reschedule, or **cancel**
6. **Rewards** — see points (including **daily login bonus**)
7. **Coupons** — list, buy, or sell on the marketplace
8. **Events & Offers** — browse and book platform events
9. **My Savings** — track savings from real order data

---

## Page URLs

| Page | URL |
|------|-----|
| Landing | http://127.0.0.1:8000/ |
| Login | http://127.0.0.1:8000/loginn/ |
| Register | http://127.0.0.1:8000/register/ |
| User Home | http://127.0.0.1:8000/ASTRAEUser/userhome/ |
| Compare / Search | http://127.0.0.1:8000/ASTRAEUser/usersearch/ |
| Deals | http://127.0.0.1:8000/ASTRAEUser/userdeals/ |
| Events & Offers | http://127.0.0.1:8000/ASTRAEUser/userevents/ |
| Book Offer | http://127.0.0.1:8000/ASTRAEUser/book/ |
| Orders | http://127.0.0.1:8000/ASTRAEUser/userorders/ |
| Coupons | http://127.0.0.1:8000/ASTRAEUser/usercoupons/ |
| Rewards | http://127.0.0.1:8000/ASTRAEUser/userrewards/ |
| My Savings | http://127.0.0.1:8000/ASTRAEUser/usersavings/ |
| Watchlist | http://127.0.0.1:8000/ASTRAEUser/userwishlist/ |
| Price Alerts | http://127.0.0.1:8000/ASTRAEUser/useralerts/ |
| Notifications | http://127.0.0.1:8000/ASTRAEUser/usernotifications/ |
| Profile | http://127.0.0.1:8000/ASTRAEUser/userprofile/ |
| Admin Dashboard | http://127.0.0.1:8000/ASTRAEAdmin/adminhome/ |
| Django Admin | http://127.0.0.1:8000/admin/ |

---

## Features Overview

| Module | Description |
|--------|-------------|
| **Unified Search** | One search bar with intelligent category detection |
| **Platform Comparison** | Side-by-side results with ASTRAE Score + AIRE ranking |
| **Why ASTRAE Recommends** | Transparent reasons (price, rating, delivery, coupon, cashback) |
| **Events & Offers** | Upcoming, live, flash sales, festival & platform-specific offers |
| **Deals Hub** | Filterable deals with deal scores |
| **Booking Flow** | Date, time slot, address, quantity, optional coupon apply |
| **Order Management** | Reschedule or cancel bookings |
| **Coupon Marketplace** | Verify, list, buy, sell with atomic transactions |
| **Apply Coupon at Booking** | Use owned coupons; marked redeemed after booking |
| **Rewards Wallet** | Points with daily login bonus and order rewards |
| **My Savings** | Real savings from orders with charts |
| **Watchlist & Alerts** | Save items and set price alerts |
| **Notifications** | In-app alerts for orders, rewards, marketplace |
| **Personalized Home** | Activity-based recommendations |
| **Admin Dashboard** | Users, orders, analytics, platform health |

### Supported platforms (demo data)

| Category | Platforms |
|----------|-----------|
| Rides | Uber, Ola, Rapido |
| Food | Swiggy, Zomato |
| Grocery | BigBasket, Zepto, Blinkit |
| Shopping | Amazon, Flipkart |
| Fashion | Myntra, Ajio |
| Beauty | Nykaa |
| Medicine | Netmeds, PharmEasy, Apollo Pharmacy |

---

## Management Commands

Run from the **`App`** folder:

```powershell
python manage.py seed_demo_data       # All demo data + demo user (recommended)
python manage.py seed_platforms       # Categories & platforms only
python manage.py seed_deals             # Demo deals
python manage.py seed_coupons           # Demo marketplace coupons
python manage.py seed_events            # Demo events & offers
python manage.py check_price_alerts     # Simulate price-drop notifications
python manage.py check                  # Django system check
python manage.py migrate                # Apply database migrations
```

---

## Project Structure

```
Astrae Unified Multi-Service Comparison and Rewards Marketplace/
├── README.md                 # This file
├── Document/                 # Project documentation (DOCX)
└── App/                      # Django application root
    ├── manage.py
    ├── requirements.txt      # Python dependencies
    ├── db.sqlite3            # SQLite database (created after migrate)
    ├── ASTRAE/               # Settings & root URLs
    ├── ASTRAEUser/           # Main app (models, views, services)
    ├── ASTRAEAdmin/           # Staff analytics dashboard
    ├── Templates/             # HTML templates
    ├── static/                # CSS, JS, images
    └── Model/                 # ML models & ChromaDB (optional)
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 6.1, SQLite |
| Frontend | Tailwind CSS (CDN), ASTRAE design system |
| Charts | Chart.js |
| ML (optional) | CatBoost, scikit-learn, ChromaDB, Sentence Transformers |
| Demo mode | Mock providers — no live third-party APIs |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `'python' is not recognized` | Install Python 3.12+ and add it to PATH, or use `py -3.12` on Windows |
| `ModuleNotFoundError: django` | Activate `venv` and run `pip install -r requirements.txt` |
| `No module named 'ASTRAE'` | Run commands from the **`App`** folder, not project root |
| Login fails for new user | In demo mode, registration is auto-active; or use `demo` / `demo123` |
| Empty search results | Run `python manage.py seed_demo_data` |
| Port 8000 already in use | Use `python manage.py runserver 8080` |
| PowerShell blocks venv activation | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once |

---

## Demo Mode Disclaimer

ASTRAE uses **simulated provider data** for development and academic presentation.

- Coupons are prefixed `DEMO-*` and marked `is_demo=True`
- Events and offers are sample data — not live external promotions
- Price alerts use deterministic demo simulation
- No real third-party API transactions occur unless explicitly integrated

The app does **not** present demo prices or offers as confirmed live data.

---

## License

Academic / educational project — © 2026 ASTRAE Team.
