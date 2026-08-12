# Django Shop Template - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Features](#features)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [API Documentation](#api-documentation)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Theming System](#theming-system)
10. [Admin Panel](#admin-panel)
11. [Contributing](#contributing)
12. [License](#license)

---

## Overview

**Django Shop Template** is a comprehensive, production-ready e-commerce template built with Django and Django REST Framework. It provides a complete foundation for building online stores with advanced features like inventory management, payment processing, shipping, discounts, and more.

### Key Features

- ✅ **Modular Architecture**: 14+ independent Django apps
- ✅ **RESTful API**: 250+ API endpoints with JWT authentication
- ✅ **Production Ready**: Docker, PostgreSQL, Redis, Celery
- ✅ **Theming System**: Customizable themes with theme/config.json
- ✅ **Admin Panel**: Custom admin interface with Persian support
- ✅ **Iranian Payment Gateways**: Zarinpal, IDPay, Pay.ir, NextPay
- ✅ **Comprehensive Testing**: 500+ test cases
- ✅ **API Documentation**: OpenAPI/Swagger support

---

## Project Structure

```
shop-template/
├── config/                          # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                # Base settings
│   │   ├── dev.py                 # Development settings
│   │   ├── test.py                # Testing settings
│   │   └── production.py          # Production settings
│   ├── urls.py                    # Main URLs
│   ├── wsgi.py
│   └── api_schema.py              # OpenAPI schema
│
├── apps/                           # Django apps
│   ├── core/                      # Core functionality
│   ├── accounts/                  # User authentication & profiles
│   ├── products/                  # Product catalog
│   ├── cart/                      # Shopping cart
│   ├── orders/                    # Order management
│   ├── payments/                  # Payment processing
│   ├── shipping/                  # Shipping methods
│   ├── inventory/                 # Inventory management
│   ├── discounts/                 # Coupons & campaigns
│   ├── blog/                      # Blog system
│   ├── reviews/                   # Product reviews
│   ├── support/                   # Customer support
│   ├── notifications/             # Notifications
│   ├── ads/                       # Advertisements
│   └── theme/                     # Theming system
│
├── static/                        # Static files
│   ├── css/
│   ├── js/
│   ├── images/
│   └── icons/
│
├── templates/                     # HTML templates
│   ├── base.html
│   ├── admin/                     # Admin templates
│   ├── store/                     # Store templates
│   └── blog/                      # Blog templates
│
├── theme/                         # Theme files
│   ├── default/
│   │   ├── config.json
│   │   ├── assets/
│   │   └── templates/
│   └── custom/
│
├── docker/                        # Docker configuration
│   ├── nginx/
│   └── Dockerfile
│
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Docker Compose
├── Dockerfile                    # Dockerfile
├── .env.example                  # Environment variables
├── pytest.ini                    # Pytest configuration
├── conftest.py                   # Pytest fixtures
├── run_tests.py                  # Test runner
└── manage.py                     # Django management script
```

---

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| **User Management** | Registration, login, profiles, addresses, wishlists |
| **Product Catalog** | Categories, brands, attributes, variations, images |
| **Shopping Cart** | Cart management, wishlist integration |
| **Order System** | Order creation, status tracking, history |
| **Payment Processing** | Multiple gateways, wallet, transactions |
| **Shipping** | Zones, methods, pickup locations, cost calculation |
| **Inventory** | Warehouses, stock management, suppliers |
| **Discounts** | Coupons, campaigns, promotional pricing |
| **Blog** | Articles, categories, comments, tags |
| **Reviews** | Ratings, comments, helpfulness voting |
| **Support** | Tickets, FAQ, customer satisfaction |
| **Notifications** | Email, push, SMS notifications |
| **Advertisements** | Banner management, placements |

### Technical Features

- **Authentication**: JWT, Session, Token-based
- **Caching**: Redis-based caching
- **Async Tasks**: Celery with Redis broker
- **Search**: Advanced search with filters
- **API Documentation**: OpenAPI/Swagger
- **Testing**: Pytest with 500+ test cases
- **Docker**: Full containerization support
- **CI/CD**: GitHub Actions ready

---

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/shop-template.git
   cd shop-template
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start containers:
   ```bash
   docker-compose up -d
   ```

4. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. Create superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. Access the application:
   - Store: http://localhost:8000
   - Admin: http://localhost:8000/admin/
   - API Docs: http://localhost:8000/api/v1/docs/

### Manual Installation

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure database:
   ```bash
   # Create PostgreSQL database
   createdb shop_template
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start development server:
   ```bash
   python manage.py runserver
   ```

---

## Configuration

### Environment Variables

Edit `.env` file with your configuration:

```env
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.dev
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SITE_URL=http://localhost:8000

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=shop_template
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@shop-template.com

# Payment Gateways
ZARINPAL_MERCHANT_ID=your-merchant-id
ZARINPAL_SANDBOX=True

IDPAY_API_KEY=your-api-key
IDPAY_SANDBOX=True

# Site Settings
SITE_NAME=Shop Template
SITE_DESCRIPTION=Professional E-commerce Template
SITE_LOGO=/static/icons/logo.svg

# Theme Settings
THEME_PRIMARY_COLOR=#2563eb
THEME_SECONDARY_COLOR=#7c3aed
```

### Settings Files

- `config/settings/dev.py` - Development settings
- `config/settings/test.py` - Testing settings
- `config/settings/production.py` - Production settings

---

## API Documentation

### Base URL

```
http://localhost:8000/api/v1/
```

### Authentication

All API endpoints require authentication using JWT tokens.

#### Get Token

```bash
POST /api/v1/accounts/login/
Content-Type: application/json

{
    "phone_number": "09123456789",
    "password": "your-password"
}

Response:
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Use Token

Add the access token to the Authorization header:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Endpoints

#### Core
- `GET /api/v1/core/settings/` - Get site settings
- `GET /api/v1/core/theme/` - Get theme configuration
- `GET /api/v1/core/health-check/` - Health check
- `POST /api/v1/core/contact/` - Submit contact form

#### Accounts
- `POST /api/v1/accounts/register/` - Register user
- `POST /api/v1/accounts/login/` - Login user
- `POST /api/v1/accounts/logout/` - Logout user
- `GET /api/v1/accounts/profile/` - Get user profile
- `PATCH /api/v1/accounts/profile/` - Update profile
- `POST /api/v1/accounts/profile/change-password/` - Change password
- `GET /api/v1/accounts/addresses/` - List addresses
- `POST /api/v1/accounts/addresses/` - Create address
- `GET /api/v1/accounts/wishlists/` - List wishlists
- `POST /api/v1/accounts/wishlists/` - Create wishlist
- `POST /api/v1/accounts/otp/request/` - Request OTP
- `POST /api/v1/accounts/otp/verify/` - Verify OTP

#### Products
- `GET /api/v1/products/` - List products
- `POST /api/v1/products/` - Create product (admin)
- `GET /api/v1/products/{slug}/` - Retrieve product
- `PATCH /api/v1/products/{slug}/` - Update product (admin)
- `DELETE /api/v1/products/{slug}/` - Delete product (admin)
- `GET /api/v1/products/categories/` - List categories
- `GET /api/v1/products/brands/` - List brands
- `GET /api/v1/products/search/` - Search products
- `GET /api/v1/products/featured/` - List featured products

#### Cart
- `GET /api/v1/cart/` - Get cart
- `POST /api/v1/cart/items/` - Add item to cart
- `PATCH /api/v1/cart/items/{id}/` - Update cart item
- `DELETE /api/v1/cart/items/{id}/` - Remove cart item
- `POST /api/v1/cart/clear/` - Clear cart
- `POST /api/v1/cart/checkout/` - Checkout

#### Orders
- `GET /api/v1/orders/` - List orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/{order_number}/` - Retrieve order
- `POST /api/v1/orders/{order_number}/cancel/` - Cancel order
- `GET /api/v1/orders/statistics/` - Order statistics (admin)

#### Payments
- `GET /api/v1/payments/gateways/` - List payment gateways
- `GET /api/v1/payments/gateways/active/` - List active gateways
- `GET /api/v1/payments/transactions/` - List transactions
- `POST /api/v1/payments/transactions/` - Create transaction
- `GET /api/v1/payments/wallet/` - Get wallet
- `POST /api/v1/payments/wallet/deposit/` - Deposit to wallet
- `POST /api/v1/payments/wallet/withdraw/` - Withdraw from wallet
- `GET /api/v1/payments/statistics/` - Payment statistics (admin)

#### Shipping
- `GET /api/v1/shipping/zones/` - List shipping zones
- `GET /api/v1/shipping/methods/` - List shipping methods
- `GET /api/v1/shipping/methods/available/` - List available methods
- `POST /api/v1/shipping/methods/cost/` - Calculate shipping cost
- `GET /api/v1/shipping/pickup-locations/` - List pickup locations
- `GET /api/v1/shipping/statistics/` - Shipping statistics (admin)

#### Inventory
- `GET /api/v1/inventory/warehouses/` - List warehouses
- `GET /api/v1/inventory/` - List inventory
- `GET /api/v1/inventory/product/{product_id}/` - Get inventory by product
- `PATCH /api/v1/inventory/{id}/` - Update inventory (admin)
- `POST /api/v1/inventory/check-stock/` - Check stock availability
- `GET /api/v1/inventory/low-stock/` - List low stock items
- `GET /api/v1/inventory/suppliers/` - List suppliers
- `GET /api/v1/inventory/purchase-orders/` - List purchase orders
- `POST /api/v1/inventory/purchase-orders/receive/{id}/` - Receive purchase order
- `GET /api/v1/inventory/statistics/` - Inventory statistics (admin)

#### Discounts
- `GET /api/v1/discounts/` - List discounts
- `GET /api/v1/discounts/coupons/` - List coupons
- `GET /api/v1/discounts/coupons/active/` - List active coupons
- `POST /api/v1/discounts/coupons/validate/` - Validate coupon
- `GET /api/v1/discounts/campaigns/` - List campaigns
- `GET /api/v1/discounts/campaigns/active/` - List active campaigns
- `GET /api/v1/discounts/statistics/` - Discount statistics (admin)

#### Blog
- `GET /api/v1/blog/categories/` - List blog categories
- `GET /api/v1/blog/tags/` - List tags
- `GET /api/v1/blog/articles/` - List articles
- `GET /api/v1/blog/articles/published/` - List published articles
- `GET /api/v1/blog/articles/featured/` - List featured articles
- `GET /api/v1/blog/articles/{slug}/` - Retrieve article
- `POST /api/v1/blog/articles/search/` - Search articles
- `GET /api/v1/blog/comments/` - List comments
- `POST /api/v1/blog/comments/` - Create comment
- `POST /api/v1/blog/comments/{id}/approve/` - Approve comment (admin)
- `GET /api/v1/blog/statistics/` - Blog statistics (admin)

#### Reviews
- `GET /api/v1/reviews/` - List reviews
- `GET /api/v1/reviews/product/{product_id}/` - List reviews for product
- `POST /api/v1/reviews/` - Create review
- `GET /api/v1/reviews/rating/{product_id}/` - Get product rating
- `POST /api/v1/reviews/{id}/approve/` - Approve review (admin)
- `GET /api/v1/reviews/comments/` - List review comments
- `POST /api/v1/reviews/comments/` - Create review comment
- `POST /api/v1/reviews/helpfulness/vote/` - Vote helpfulness
- `GET /api/v1/reviews/statistics/` - Review statistics (admin)

#### Support
- `GET /api/v1/support/categories/` - List support categories
- `GET /api/v1/support/tickets/` - List tickets
- `POST /api/v1/support/tickets/` - Create ticket
- `GET /api/v1/support/tickets/{ticket_number}/` - Retrieve ticket
- `POST /api/v1/support/tickets/{ticket_number}/close/` - Close ticket
- `GET /api/v1/support/messages/` - List ticket messages
- `POST /api/v1/support/messages/` - Create ticket message
- `GET /api/v1/support/faq/` - List FAQs
- `GET /api/v1/support/faq/categories/` - List FAQ categories
- `POST /api/v1/support/satisfaction/` - Submit satisfaction
- `GET /api/v1/support/statistics/` - Support statistics (admin)

#### Notifications
- `GET /api/v1/notifications/` - List notifications
- `GET /api/v1/notifications/unread/` - List unread notifications
- `POST /api/v1/notifications/{id}/mark-read/` - Mark as read
- `POST /api/v1/notifications/mark-all-read/` - Mark all as read
- `DELETE /api/v1/notifications/{id}/` - Delete notification
- `GET /api/v1/notifications/templates/` - List templates (admin)
- `GET /api/v1/notifications/emails/` - List email notifications (admin)
- `POST /api/v1/notifications/emails/{id}/send/` - Send email (admin)
- `GET /api/v1/notifications/push/` - List push notifications (admin)
- `POST /api/v1/notifications/push/{id}/send/` - Send push (admin)
- `GET /api/v1/notifications/sms/` - List SMS notifications (admin)
- `POST /api/v1/notifications/sms/{id}/send/` - Send SMS (admin)
- `POST /api/v1/notifications/device-tokens/register/` - Register device token
- `GET /api/v1/notifications/device-tokens/` - List device tokens
- `POST /api/v1/notifications/device-tokens/{token}/remove/` - Remove device token
- `GET /api/v1/notifications/statistics/` - Notification statistics (admin)

#### Ads
- `GET /api/v1/ads/` - List advertisements
- `GET /api/v1/ads/placements/` - List ad placements
- `GET /api/v1/ads/placements/{placement}/` - Get ads by placement
- `POST /api/v1/ads/impressions/` - Track impression
- `POST /api/v1/ads/clicks/` - Track click
- `GET /api/v1/ads/statistics/` - Ad statistics (admin)

---

## Testing

### Running Tests

#### All Tests
```bash
python run_tests.py
```

#### Specific App
```bash
python run_tests.py accounts
python run_tests.py products
python run_tests.py orders
```

#### With Coverage
```bash
python run_tests.py --coverage
```

#### Verbose Output
```bash
python run_tests.py --verbose
```

#### Specific Test Type
```bash
python run_tests.py --markers api      # Only API tests
python run_tests.py --markers unit     # Only unit tests
python run_tests.py --markers integration  # Only integration tests
```

### Test Structure

All tests are located in the `apps/<app>/tests/` directory:

```
apps/accounts/tests/
├── __init__.py
└── test_api.py          # API endpoint tests

apps/products/tests/
├── __init__.py
└── test_api.py          # API endpoint tests

# ... and so on for all apps
```

### Test Coverage

The project includes comprehensive tests for:

- ✅ All API endpoints
- ✅ Authentication and authorization
- ✅ Model creation and validation
- ✅ Serializer validation
- ✅ View permissions
- ✅ Edge cases and error handling

---

## Deployment

### Docker Deployment

1. Build and start containers:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```

2. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. Collect static files:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

4. Create superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Production Settings

Use `config.settings.production` for production:

```python
# In docker-compose.prod.yml or settings
DJANGO_SETTINGS_MODULE=config.settings.production
```

### Gunicorn Configuration

For production, use Gunicorn as the application server:

```bash
# In Dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120", "config.wsgi:application"]
```

### Nginx Configuration

Configure Nginx as a reverse proxy:

```nginx
# docker/nginx/conf.d/django.conf
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /app/staticfiles/;
    }
    
    location /media/ {
        alias /app/media/;
    }
}
```

---

## Theming System

### Theme Structure

Themes are located in the `theme/` directory:

```
theme/
├── default/                      # Default theme
│   ├── config.json              # Theme configuration
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/
│       ├── base.html
│       ├── store/
│       └── admin/
└── custom/                      # Custom theme (optional)
    ├── config.json
    └── assets/
```

### Theme Configuration (config.json)

```json
{
    "name": "Default Theme",
    "version": "1.0.0",
    "author": "Shop Template",
    "description": "Default theme for Shop Template",
    "colors": {
        "primary": "#2563eb",
        "secondary": "#7c3aed",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "info": "#06b6d4",
        "light": "#f8fafc",
        "dark": "#1e293b"
    },
    "fonts": {
        "primary": "Inter",
        "secondary": "Vazir",
        "fallback": "sans-serif"
    },
    "direction": "rtl",
    "layout": {
        "header": "fixed",
        "sidebar": "collapsible",
        "footer": "fixed"
    },
    "features": {
        "dark_mode": true,
        "animations": true,
        "lazy_loading": true
    }
}
```

### Creating a Custom Theme

1. Create a new directory in `theme/`:
   ```bash
   mkdir -p theme/my-theme/assets/css
   mkdir -p theme/my-theme/templates
   ```

2. Create `config.json`:
   ```json
   {
       "name": "My Theme",
       "version": "1.0.0",
       "colors": {
           "primary": "#3b82f6"
       }
   }
   ```

3. Update settings to use your theme:
   ```python
   # config/settings/base.py
   THEME_NAME = 'my-theme'
   ```

---

## Admin Panel

### Access

- URL: `/admin/`
- Use superuser credentials to login

### Custom Admin Features

The project includes a custom admin panel with:

- ✅ Persian language support
- ✅ RTL layout
- ✅ Custom dashboard
- ✅ Advanced filters
- ✅ Export/Import functionality
- ✅ Custom actions

### Admin Customization

Custom admin files are located in `apps/theme/admin/`:

```python
# apps/theme/admin/dashboard.py
from django.contrib import admin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class CustomDashboardAdmin(admin.AdminSite):
    site_header = _('Shop Template Admin')
    site_title = _('Shop Template Admin')
    index_title = _('Dashboard')
    
    def get_app_list(self, request):
        # Custom app ordering
        app_list = super().get_app_list(request)
        # Sort apps as needed
        return sorted(app_list, key=lambda x: x['name'])

# Register custom dashboard views
# admin.site.register_view(...)
```

---

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Make your changes
4. Run tests:
   ```bash
   python run_tests.py
   ```
5. Commit your changes:
   ```bash
   git commit -m 'Add your feature'
   ```
6. Push to the branch:
   ```bash
   git push origin feature/your-feature
   ```
7. Open a pull request

### Coding Standards

- Follow PEP 8 guidelines
- Use type hints where possible
- Write comprehensive docstrings
- Include tests for new features
- Keep commits atomic and well-documented

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

For support and questions:

- **Documentation**: https://shop-template.com/docs/
- **Issues**: https://github.com/your-username/shop-template/issues
- **Email**: support@shop-template.com

---

*Last updated: August 11, 2026*
