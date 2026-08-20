IN YOUR SOUL — Commercial Website

Egyptian underground streetwear e-commerce platform.

In Your Soul is a full-stack commercial fashion platform built around an underground streetwear identity, combining a dark cyberpunk-inspired interface with a complete shopping, account, payment, and administration system.

Formerly known as FREKS.

⸻

Stack

* Backend: Flask (Python), SQLAlchemy ORM
* Authentication: Flask-Login, custom token-based session validation
* Security: Flask-WTF (CSRF), Flask-Limiter (rate limiting), password hashing
* Database: PostgreSQL via Supabase (production) / SQLite (local fallback)
* Frontend: Jinja2 templates, vanilla JavaScript, custom CSS
* Typography: Space Mono + Space Grotesk
* Deployment: Gunicorn + Railway
* Email: Resend API
* Design System: In Your Soul — dark underground aesthetic with neon-lime accents

⸻

Features

Store

* Dark immersive homepage
* Responsive mobile-first interface
* Product catalog and categories
* Product detail pages
* Multiple product images
* Size and variant selection
* Live inventory tracking
* Add to cart
* Update and remove cart items
* Persistent shopping cart
* Checkout system
* Saved customer addresses
* Order history

Payments

Supported payment methods include:

* Cash on Delivery
* Vodafone Cash
* InstaPay

Online-payment orders use a payment confirmation window. Unpaid orders can automatically expire and return reserved inventory to stock.

⸻

User Accounts

* Username-based authentication
* Phone number registration
* Secure password hashing
* Email verification
* Login / logout
* Password changes
* Profile management
* Address management
* Default address selection
* Order history
* Order status tracking

Order statuses:

Pending
   ↓
Confirmed
   ↓
Shipped
   ↓
Delivered

⸻

Email Verification

Production email delivery uses the Resend API.

Verification emails are sent during account registration and contain time-limited verification codes.

Required environment variables:

RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=your_verified_sender

Never commit API keys or other credentials to Git.

⸻

Security

The application includes multiple security layers:

* Token-based session validation
* Fresh authentication token on login
* Immediate session invalidation on logout
* CSRF protection on forms
* Rate limiting on authentication and sensitive routes
* Secure password hashing
* Payment-method whitelisting
* Server-side validation
* Protected admin routes
* Environment-based secret configuration

Authentication tokens are validated through the custom authentication guard before protected actions are processed.

⸻

Admin Dashboard

The /admin dashboard provides administrative control over the store.

Dashboard

* Revenue statistics
* Order statistics
* User statistics
* Product statistics

Products

* Create products
* Edit products
* Activate/deactivate products
* Manage variants
* Manage inventory
* Manage product images

Inventory

Inventory can be managed per size and variant, including:

XS
S
M
L
XL
XXL

Orders

* View customer orders
* Update order status
* Review payment information
* Manage order workflow

Categories

* Create categories
* Edit categories
* Manage product categorization

Users

* View users
* Manage accounts
* Promote/demote administrators

⸻

Database

Production uses PostgreSQL hosted through Supabase.

Local development can use SQLite automatically when DATABASE_URL is not provided.

Production

Create a .env file:

SECRET_KEY=your-strong-random-secret-key
DATABASE_URL=postgresql+psycopg://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@YOUR_POOLER_HOST:6543/postgres
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=your_verified_sender

Generate a secure secret key:

python -c "import secrets; print(secrets.token_hex(32))"

Supabase

The PostgreSQL connection uses the psycopg driver:

postgresql+psycopg://

When using Supabase’s pooler, prepared statements are disabled through SQLAlchemy’s connection configuration.

⸻

Local Development

1. Clone the repository

git clone REPOSITORY_URL
cd in-your-soul

2. Create a virtual environment

Windows

python -m venv .venv
.venv\Scripts\activate

macOS / Linux

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

Create:

.env

Example:

SECRET_KEY=your-secret-key
# Optional locally — SQLite is used automatically if omitted
DATABASE_URL=postgresql+psycopg://...
# Email verification
RESEND_API_KEY=your_api_key
RESEND_FROM_EMAIL=your_verified_sender

5. Create database tables

python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

6. Seed the database

python seed.py

7. Start the development server

python run.py

Open:

http://localhost:5000

⸻

Project Structure

in-your-soul/
├── run.py
├── seed.py
├── config.py
├── requirements.txt
├── README.md
└── app/
    ├── __init__.py
    ├── auth_guard.py
    │
    ├── models/
    │   └── __init__.py
    │
    ├── routes/
    │   ├── main.py
    │   ├── auth.py
    │   ├── cart.py
    │   ├── account.py
    │   └── admin.py
    │
    ├── static/
    │   ├── css/
    │   │   └── main.css
    │   ├── js/
    │   │   └── main.js
    │   └── images/
    │       └── products/
    │
    └── templates/
        ├── base.html
        ├── errors/
        ├── main/
        ├── auth/
        ├── account/
        └── admin/

⸻

Deployment

The production application is designed to run with:

Flask
   ↓
Gunicorn
   ↓
Railway
   ↓
Supabase PostgreSQL

Production checklist

* Set a strong SECRET_KEY
* Configure the production DATABASE_URL
* Configure Resend
* Set production environment variables
* Disable debug mode
* Use Gunicorn
* Enable HTTPS
* Enable secure session cookies
* Configure persistent rate-limit storage
* Protect admin access
* Never commit .env or API keys

Example Gunicorn command:

gunicorn run:app

⸻

Design System

The original Jungle System visual language evolved into the current In Your Soul identity.

Core Palette

Token	Value	Usage
--bg	#040804	Main background
--panel	#0b180b	Cards and panels
--panel-2	#0e1d0e	Secondary surfaces
--accent	#76ff03	CTAs, prices, highlights
--accent-dim	#4db800	Secondary accent
--danger	#ff1744	Errors and alerts
--muted	#3a4a3a	Borders and disabled states

Typography

Space Mono
Space Grotesk

The visual direction focuses on:

* Underground streetwear
* Cyberpunk-inspired interfaces
* High contrast
* Neon accents
* Minimal surfaces
* Aggressive typography
* Mobile-first interaction

⸻

Project Evolution

FREKS
  │
  │ Rebrand
  ▼
IN YOUR SOUL

The underlying application architecture remains the same while the brand identity, visual direction, and commercial presentation evolved into In Your Soul.

⸻

Author

AxIbrahim

Built in 2026.

In Your Soul — Wear what lives inside.