# FREKS — Commercial Website

Egyptian underground streetwear e-commerce platform.
Built with Flask, SQLAlchemy, and the Jungle System design language.

---

## Stack

- **Backend**: Flask (Python), SQLAlchemy ORM, Flask-Login, Flask-Bcrypt, Flask-WTF (CSRF), Flask-Limiter (rate limiting)
- **Database**: PostgreSQL via Supabase (production) / SQLite (local fallback)
- **Frontend**: Jinja2 templates, pure CSS (Space Mono + Space Grotesk), vanilla JS
- **Design**: Jungle System — Lime `#76ff03` on pitch black `#040804`
- **Security**: Token-based session validation, rate-limited auth routes, CSRF protection

---

## Setup

### 1. Clone the repository

```bash
git clone REPOSITORY_URL
cd freks
```

### 2. Create virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Create a `.env` file in the project root:

```dotenv
SECRET_KEY=your-strong-random-secret-key-here
DATABASE_URL=postgresql+psycopg://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-1-eu-central-1.pooler.supabase.com:6543/postgres
```

To generate a strong secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Get your Supabase connection string:**
1. Go to your Supabase project → Project Settings → Database → Connection String
2. Choose **Transaction pooler** or **Session pooler** (port `6543`)
3. Use the `+psycopg` driver prefix (not `+psycopg2`) and replace `[YOUR-PASSWORD]` with your real password
4. If your password contains special characters, URL-encode them (e.g. `\` → `%5C`, `@` → `%40`)

No `.env`? The app falls back to local SQLite automatically — fine for quick testing, not for production.

### 5. Create database tables

```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 6. Seed the database

```bash
python seed.py
```

### 7. Run the server

```bash
python run.py
```

Visit: `http://localhost:5000`

---

## Default Credentials

| Role  | Username     | Password    |
|-------|--------------|-------------|
| Admin | freks_admin  | Freks@2025! |
| Demo  | jungle_user  | Demo@2025!  |

**Change these immediately in production.** Login is username-based (not email) — registration collects phone number instead of email, matching the Egyptian market (Vodafone Cash / InstaPay tie to phone numbers).

---

## Features

### Store
- Video hero homepage with cyber-rain matrix canvas effect
- Product grid with hover image swap, live stock indicators
- Product detail page with size selector, add-to-cart
- Full cart management (add, update, remove)
- Checkout with saved or manual address entry

### Payments
- Cash on Delivery (COD)
- Vodafone Cash — number: `01557793954`
- InstaPay
- 2-hour payment window for Vodafone Cash / InstaPay orders — unpaid orders auto-cancel and restock automatically
- 14-day return policy displayed on every order

### User Accounts
- Register / Login / Logout (username + phone based)
- Order history with visual status tracking (pending → confirmed → shipped → delivered)
- Address management (add, remove, set default)
- Profile editing + password change

### Security
- Token-based session validation (`app/auth_guard.py`) — every login issues a fresh token; logout or token mismatch instantly invalidates the session
- Rate limiting on login (5/min), registration (3/hour), cart actions, and checkout to prevent brute-force and bot abuse
- CSRF protection on all forms via Flask-WTF
- Payment method whitelisting at checkout

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
├── config.py                # Configuration (env, DB, engine options)
├── requirements.txt
├── README.md
└── app/
    ├── __init__.py          # App factory
    ├── auth_guard.py        # Token-based session security layer
    ├── models/
    │   └── __init__.py      # All SQLAlchemy models
    ├── routes/
    │   ├── main.py           # Public shop routes + expired order cleanup
    │   ├── auth.py            # Login / register / logout
    │   ├── cart.py             # Cart & checkout
    │   ├── account.py          # User account pages
    │   └── admin.py             # Admin dashboard
    ├── static/
    │   ├── css/main.css       # Jungle System design system
    │   ├── js/main.js          # All frontend JS
    │   ├── images/
    │   │   └── products/        # Uploaded product images
    │   └── videos/
    │       └── hero.mp4          # Homepage background video (.mp4 required)
    └── templates/
        ├── base.html           # Global layout + nav + footer
        ├── errors/               # 429 rate-limit error page
        ├── main/                  # Shop, product, cart, checkout, about
        ├── auth/                   # Login, register
        ├── account/                 # Dashboard, orders, addresses, profile
        └── admin/                    # Admin panel templates
```

---

## Hero Video

Place your video at:
```
app/static/videos/hero.mp4
```

Recommended: 1920×1080, H.264, under 20MB, dark/moody content. The cyber-rain matrix canvas renders automatically as a fallback if no video is loaded.

---

## Database Notes — Supabase / Postgres

This project uses `psycopg` (v3) as the Postgres driver. Two things matter for Supabase's connection pooler to work correctly:

1. **Driver prefix in the URL must be `+psycopg`**, not `+psycopg2`:
   ```
   postgresql+psycopg://...
   ```
2. **Prepared statements must be disabled** when using Supabase's pooler (PgBouncer doesn't support them). This is already configured in `config.py` via:
   ```python
   SQLALCHEMY_ENGINE_OPTIONS = {
       "connect_args": {"prepare_threshold": None}
   }
   ```
   Don't pass `prepare_threshold` as a URL query string — psycopg3 parses it as a string and crashes; it must be set as a Python `None` via `connect_args`.

If switching back to local SQLite for testing, just remove `DATABASE_URL` from `.env` — the app falls back automatically.

---

## Production Deployment Checklist

- [ ] Set `SECRET_KEY` to a strong random value (never commit this)
- [ ] Set `DATABASE_URL` to your production PostgreSQL/Supabase connection string
- [ ] Change default admin/demo credentials
- [ ] Set `DEBUG=False`
- [ ] Use `gunicorn run:app` behind nginx
- [ ] Configure a persistent rate-limiter storage backend (Redis recommended) instead of in-memory
- [ ] Restrict `/admin` access by IP or additional auth layer
- [ ] Set `SESSION_COOKIE_SECURE = True` once running behind HTTPS

---

## Color Palette — Jungle System

| Token      | Value     | Usage                        |
|------------|-----------|-------------------------------|
| `--bg`     | `#040804` | Page background               |
| `--panel`  | `#0b180b` | Cards, panels, sidebar        |
| `--accent` | `#76ff03` | Primary accent, CTAs, prices  |
| `--danger` | `#ff1744` | Errors, sold-out, alerts      |
| `--muted`  | `#3a4a3a` | Disabled states, borders      |

---

@ Made by AxIbrahim — 2026