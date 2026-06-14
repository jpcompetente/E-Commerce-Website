# E-Commerce Website

A Django-based multi-vendor marketplace for students and small businesses. The system supports buyers, vendors, store applications, product catalogs, carts, orders, payments, reviews, payouts, and buyer/vendor messaging models.

## Current Stack

- Python with Django 4.2.16
- SQLite by default, with PostgreSQL support through `DATABASE_URL`
- Django Allauth for email-based authentication
- Crispy Forms with Bootstrap 5
- Stripe payment integration
- WhiteNoise for static file serving
- Pillow for image uploads
- django-mptt for category trees
- django-taggit for product tags
- django-filter for filtering support

## Project Structure

```text
E-Commerce-Website/
├── apps/
│   ├── users/       # Custom user model and addresses
│   ├── vendors/     # Stores, vendor applications, store policies, dashboard views
│   ├── products/    # Categories, products, variants, images, wishlist
│   ├── orders/      # Cart, checkout, orders, sub-orders, order items
│   ├── payments/    # Stripe/COD payments and vendor payouts
│   ├── reviews/     # Product and store reviews
│   └── messaging/   # Buyer-store conversations and messages
├── marketplace/     # Django settings, root URLs, ASGI/WSGI
├── media/           # Uploaded media files
├── static/          # Project static files
├── templates/       # Project templates
├── manage.py
├── requirements.txt
└── README.md
```

## Features Implemented

- Custom email-login user model with buyer and vendor roles
- User addresses with default-address handling
- Vendor application flow and store approval status
- Vendor dashboard with revenue, order, low-stock, product, and earnings views
- Store pages with products, reviews, and policies
- Product browsing, search, category filtering, price filtering, sorting, and pagination
- Product detail pages with related products, variants, images, approved reviews, and view counts
- Wishlist add/remove support for authenticated users
- Session carts for guests and account carts for signed-in users
- Checkout flow that splits orders by vendor into sub-orders
- Marketplace commission calculation with vendor earnings
- Stripe PaymentIntent checkout and Stripe webhook handling
- Cash on delivery payment option
- Vendor payout records after successful or confirmed payment
- Data models for product reviews, store reviews, review replies, conversations, and messages

## Current Routes

| Path | App | Purpose |
| --- | --- | --- |
| `/` | products | Home page |
| `/shop/` | products | Product listing, search, filters, sorting |
| `/product/<slug>/` | products | Product detail |
| `/wishlist/` | products | User wishlist |
| `/vendors/store/<slug>/` | vendors | Store detail |
| `/vendors/apply/` | vendors | Vendor application |
| `/vendors/apply/status/` | vendors | Vendor application status |
| `/vendors/dashboard/` | vendors | Vendor dashboard |
| `/vendors/dashboard/products/` | vendors | Vendor product management |
| `/vendors/dashboard/orders/` | vendors | Vendor order management |
| `/vendors/dashboard/earnings/` | vendors | Vendor earnings |
| `/orders/cart/` | orders | Shopping cart |
| `/orders/checkout/` | orders | Checkout |
| `/orders/place/` | orders | Place order |
| `/orders/my-orders/` | orders | Buyer order history |
| `/payments/checkout/<order_id>/` | payments | Payment checkout |
| `/payments/success/<order_id>/` | payments | Payment success |
| `/payments/webhook/` | payments | Stripe webhook |
| `/accounts/` | allauth | Authentication routes |
| `/admin/` | admin | Django admin |

> Note: `users`, `reviews`, and `messaging` currently include data models, but their public URL files are placeholders.

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root.

```env
SECRET_KEY=replace-with-a-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

STRIPE_PUBLIC_KEY=pk_test_placeholder
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_WEBHOOK_SECRET=whsec_placeholder

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@marketplace.com
```

4. Run migrations.

```bash
python manage.py migrate
```

5. Create an admin user.

```bash
python manage.py createsuperuser
```

6. Start the development server.

```bash
python manage.py runserver
```

Open the app at `http://127.0.0.1:8000/`.

## Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| `SECRET_KEY` | Django secret key | Development fallback in settings |
| `DEBUG` | Enables debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Database connection URL | `sqlite:///db.sqlite3` |
| `STRIPE_PUBLIC_KEY` | Stripe publishable key | `pk_test_placeholder` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_placeholder` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_placeholder` |
| `EMAIL_BACKEND` | Django email backend | Console backend |
| `DEFAULT_FROM_EMAIL` | Sender address for system emails | `noreply@marketplace.com` |

## Development Notes

- The custom user model is `users.User`, so migrations should be created carefully before changing user fields.
- The default database is SQLite, but `psycopg2-binary` is installed for PostgreSQL deployments.
- Static files are configured with WhiteNoise and `CompressedManifestStaticFilesStorage`.
- Media uploads are stored locally in `media/` during development.
- The marketplace commission rate is currently set to `0.05` in `marketplace/settings.py`.
- Templates and static directories exist, but this repo currently does not include template or static files.

## Useful Commands

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
python manage.py test
```
