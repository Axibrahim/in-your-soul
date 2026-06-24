# FREKS — Jungle System

Egyptian underground streetwear e-commerce platform.  
Built with Flask, SQLAlchemy, and the Jungle System design language.

---

## Stack

- **Backend**: Flask (Python), SQLAlchemy ORM, Flask-Login, Flask-Bcrypt, Flask-WTF (CSRF)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Jinja2 templates, pure CSS (Space Mono + Space Grotesk), vanilla JS
- **Design**: Jungle System — Lime `#76ff03` on pitch black `#040804`

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
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///freks.db   # or postgresql://...
```

### 4. Initialize and seed the database
```bash
python seed.py
```

### 5. Run the server
```bash
python run.py
```

Visit: `http://localhost:5000`

---

## Default Credentials

| Role  | Email            | Password     |
|-------|------------------|-------------|
| Admin | admin@freks.eg   | Freks@2025! |
| Demo  | demo@freks.eg    | Demo@2025!  |

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
    │       └── hero.mp4    # Homepage hero video (add your own)
    └── templates/
        ├── base.html       # Global layout + nav + footer
        ├── main/           # Shop, product, cart, checkout, about
        ├── auth/           # Login, register
        ├── account/        # Dashboard, orders, addresses, profile
        └── admin/          # Admin panel templates
```

---

## Hero Video

Place your video at:
```
app/static/videos/hero.mp4
```

Recommended: 1920×1080, H.264, under 20MB, dark/moody content.  
The cyber-rain matrix canvas will render as a fallback if no video is loaded.

---

## Production Deployment

1. Set `SECRET_KEY` to a strong random value
2. Set `DATABASE_URL` to your PostgreSQL connection string
3. Use `gunicorn run:app` behind nginx
4. Set `DEBUG=False`
5. Configure file upload storage (S3 recommended for images)

---

## Color Palette — Jungle System

| Token     | Value     | Usage                        |
|-----------|-----------|------------------------------|
| `--bg`    | `#040804` | Page background              |
| `--panel` | `#0b180b` | Cards, panels, sidebar       |
| `--accent`| `#76ff03` | Primary accent, CTAs, prices |
| `--danger`| `#ff1744` | Errors, sold-out, alerts     |
| `--muted` | `#3a4a3a` | Disabled states, borders     |
