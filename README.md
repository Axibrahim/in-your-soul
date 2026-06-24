# FREKS — Commercial Website

Egyptian underground streetwear e-commerce platform.  
Built with Flask, SQLAlchemy, and Authentic System design.

---

## Stack

- **Backend**: Flask (Python), SQLAlchemy ORM, Flask-Login, Flask-Bcrypt, Flask-WTF (CSRF)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Jinja2 templates, pure CSS (Space Mono + Space Grotesk), vanilla JS
- **Design**: Void Energetic System — Lime `#76ff03` on pitch black `#040804`

---

## Setup

### 1. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate        # Linux / Mac
.venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment (optional)
Create a `.env` file or set env vars:
```bash
SECRET_KEY=server_test_secret_key
DATABASE_URL=sqlite:///freks.db

// For college //

git clone REPOSITORY_URL
cd PROJECT_NAME

# Windows
python -m venv venv
venv\Scripts\activate

# macOS
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python run.py
```

### 5. Run the server
```bash
python run.py
```

Visit: `http://localhost:5000`

---

## Default Credentials

| Role  | User name            | Password     |
|-------|------------------|-------------|
| Admin | bahz   | Amro4488348 |
| Demo  | joo    | Yousef 4488348  |

**Change these immediately in production.**

---

## Features

### Store
- Video hero homepage with cyber-rain matrix effect
- Product grid with hover image swap, live stock indicators
- Product detail with size selector, add-to-cart
- Full cart management (add, update, remove)
- Checkout with address management

### Payments
- Cash on Delivery (COD)
- Vodafone Cash — number: `01557793954`
- InstaPay

### User Accounts
- Register / Login / Logout
- Order history with status tracking
- Address management (add, remove, set default)
- Profile editing + password change

### Admin Dashboard (`/admin`)
- Sales stats overview (orders, revenue, users, products)
- Product management: add, edit, toggle active/inactive
- Per-size inventory management (XS → XXL)
- Order management with status updates
- Category management
- User management (promote/demote admin)

---

## Project Structure

```
freks/
├── run.py                  # App entry point
├── seed.py                 # Database seeder
├── config.py               # Configuration
├── requirements.txt
├── README.md
└── app/
    ├── __init__.py         # App factory
    ├── models/
    │   └── __init__.py     # All SQLAlchemy models
    ├── routes/
    │   ├── main.py         # Public shop routes
    │   ├── auth.py         # Login/register/logout
    │   ├── cart.py         # Cart & checkout
    │   ├── account.py      # User account pages
    │   └── admin.py        # Admin dashboard
    ├── static/
    │   ├── css/main.css    # Jungle System design system
    │   ├── js/main.js      # All frontend JS
    │   ├── images/
    │   │   └── products/   # Uploaded product images
    │   └── videos/
    │       └── hero.mp4    # Homepage video (mp4 Video required)
    └── templates/
        ├── base.html       # Global layout + nav + footer
        ├── main/           # Shop, product, cart, checkout, about
        ├── auth/           # Login, register
        ├── account/        # Dashboard, orders, addresses, profile
        └── admin/          # Admin panel templates
```

---

## Hero Video

Place video at:
```
app/static/videos/hero.mp4

```

---

## Production Deployment Requirements

1. Set `SECRET_KEY` to a strong random password
2. Set `DATABASE_URL` to PostgreSQL connection string
3. Use `gunicorn run:app` behind nginx
4. Set `DEBUG=False`

---

## Color Palette — Jungle System

| Token     | Value     | Usage                        |
|-----------|-----------|------------------------------|
| `--bg`    | `#040804` | Page background              |
| `--panel` | `#0b180b` | Cards, panels, sidebar       |
| `--accent`| `#76ff03` | Primary accent, CTAs, prices |
| `--danger`| `#ff1744` | Errors, sold-out, alerts     |
| `--muted` | `#3a4a3a` | Disabled states, borders     |
