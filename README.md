# Django Shop Template

> **Professional, Resellable E-commerce Template for Django**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.0+](https://img.shields.io/badge/django-5.0+-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-orange.svg)](https://pep8.org/)

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/shop-template.git
cd shop-template

# Copy environment file
cp .env.example .env

# Start containers
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access the application
# Store: http://localhost:8000
# Admin: http://localhost:8000/admin/
# API Docs: http://localhost:8000/api/v1/docs/
```

### Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database (PostgreSQL required)
createdb shop_template

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

---

## ✨ Features

### Core Features

- 🛒 **E-commerce Ready**: Complete shopping cart, checkout, and order management
- 📦 **Product Catalog**: Categories, brands, attributes, variations, images
- 💳 **Payment Processing**: Multiple Iranian gateways (Zarinpal, IDPay, Pay.ir, NextPay)
- 🚚 **Shipping**: Zones, methods, pickup locations, cost calculation
- 📊 **Inventory**: Warehouses, stock management, suppliers, purchase orders
- 🎁 **Discounts**: Coupons, campaigns, promotional pricing
- ✍️ **Blog**: Articles, categories, tags, comments
- ⭐ **Reviews**: Ratings, comments, helpfulness voting
- 🎧 **Support**: Tickets, FAQ, customer satisfaction
- 🔔 **Notifications**: Email, push, SMS notifications
- 📢 **Advertisements**: Banner management, placements, tracking

### Technical Features

- 🔧 **Modular Architecture**: 14+ independent Django apps
- 🌐 **RESTful API**: 250+ endpoints with JWT authentication
- 🐳 **Docker Ready**: Full containerization with Docker Compose
- 🐘 **PostgreSQL**: Production-ready database
- 🚀 **Redis**: Caching and message broker
- ⚡ **Celery**: Async task processing
- 📝 **API Docs**: OpenAPI/Swagger documentation
- 🧪 **Tested**: 500+ test cases, comprehensive coverage
- 🌍 **International**: Persian language support, RTL layout
- 🎨 **Theming**: Customizable themes with config.json
- 👨‍💼 **Admin Panel**: Custom admin interface

---

## 📂 Project Structure

```
shop-template/
├── config/                          # Django project configuration
│   ├── settings/                  # Environment-specific settings
│   │   ├── base.py               # Base settings
│   │   ├── dev.py                # Development settings
│   │   ├── test.py               # Testing settings
│   │   └── production.py         # Production settings
│   ├── urls.py                   # Main URL routing
│   └── api_schema.py             # OpenAPI schema
│
├── apps/                           # Django applications
│   ├── core/                     # Core functionality
│   ├── accounts/                 # User management
│   ├── products/                 # Product catalog
│   ├── cart/                     # Shopping cart
│   ├── orders/                   # Order management
│   ├── payments/                 # Payment processing
│   ├── shipping/                 # Shipping management
│   ├── inventory/                # Inventory management
│   ├── discounts/                # Discounts & coupons
│   ├── blog/                     # Blog system
│   ├── reviews/                  # Product reviews
│   ├── support/                  # Customer support
│   ├── notifications/            # Notifications
│   └── ads/                      # Advertisements
│
├── theme/                         # Theming system
│   └── default/
│       ├── config.json           # Theme configuration
│       └── assets/               # Theme assets
│
├── docker/                        # Docker configuration
│   └── nginx/                    # Nginx proxy config
│
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Docker Compose
├── Dockerfile                   # Dockerfile
├── .env.example                 # Environment template
├── pytest.ini                   # Test configuration
├── run_tests.py                 # Test runner
├── DOCUMENTATION.md             # Full documentation
└── README.md                    # This file
```

---

## 📊 API Documentation

### Base URL
```
http://localhost:8000/api/v1/
```

### Authentication
All API endpoints require JWT authentication.

**Get Token:**
```bash
POST /api/v1/accounts/login/
{
    "phone_number": "09123456789",
    "password": "your-password"
}
```

**Use Token:**
```bash
Authorization: Bearer <your-access-token>
```

### API Endpoints

| Module | Endpoints | Description |
|--------|-----------|-------------|
| **Core** | 4 | Site settings, theme, health check |
| **Accounts** | 20+ | User auth, profiles, addresses, wishlists |
| **Products** | 25+ | Products, categories, brands, search |
| **Cart** | 15+ | Cart management, checkout |
| **Orders** | 20+ | Order creation, tracking, history |
| **Payments** | 15+ | Gateways, transactions, wallet |
| **Shipping** | 15+ | Zones, methods, cost calculation |
| **Inventory** | 20+ | Warehouses, stock, suppliers |
| **Discounts** | 15+ | Coupons, campaigns, validation |
| **Blog** | 25+ | Articles, categories, comments |
| **Reviews** | 20+ | Ratings, comments, helpfulness |
| **Support** | 30+ | Tickets, FAQ, satisfaction |
| **Notifications** | 25+ | Email, push, SMS, device tokens |
| **Ads** | 10+ | Banners, placements, tracking |

**Total: 250+ API Endpoints**

### Full API Documentation

Access interactive API documentation at:
```
http://localhost:8000/api/v1/docs/
```

Or see `DOCUMENTATION.md` for detailed endpoint documentation.

---

## 🧪 Testing

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Tests
```bash
# Test specific app
python run_tests.py accounts
python run_tests.py products

# With coverage
python run_tests.py --coverage

# Verbose output
python run_tests.py --verbose
```

### Test Statistics
- **Total Tests:** 500+
- **Coverage:** All API endpoints, models, serializers, views
- **Pass Rate:** 100% (all tests passing)

---

## 🎨 Theming System

### Theme Configuration

Themes are configured via `theme/<theme-name>/config.json`:

```json
{
    "name": "Default Theme",
    "version": "1.0.0",
    "colors": {
        "primary": "#2563eb",
        "secondary": "#7c3aed",
        "success": "#10b981",
        "danger": "#ef4444"
    },
    "fonts": {
        "primary": "Inter",
        "secondary": "Vazir"
    },
    "direction": "rtl",
    "features": {
        "dark_mode": true,
        "animations": true
    }
}
```

### Create Custom Theme

1. Create theme directory:
   ```bash
   mkdir -p theme/my-theme/assets
   ```

2. Create `config.json` with your settings

3. Update Django settings:
   ```python
   THEME_NAME = 'my-theme'
   ```

---

## 🌍 Internationalization

### Persian Language Support
- ✅ RTL layout support
- ✅ Persian date formatting
- ✅ Persian number formatting
- ✅ Persian calendar support
- ✅ Iranian payment gateways

### Language Configuration
```python
# config/settings/base.py
LANGUAGE_CODE = 'fa-ir'
LANGUAGES = [
    ('fa', 'Persian'),
    ('en', 'English'),
]
```

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SITE_URL=http://localhost:8000

# Database
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
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Payment Gateways
ZARINPAL_MERCHANT_ID=your-merchant-id
IDPAY_API_KEY=your-api-key
```

---

## 📦 Deployment

### Docker Deployment

```bash
# Build and start
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Production Settings

Use `config.settings.production`:

```python
# In docker-compose.prod.yml
environment:
  - DJANGO_SETTINGS_MODULE=config.settings.production
```

---

## 📚 Documentation

- [Full Documentation](DOCUMENTATION.md) - Complete project documentation
- [API Documentation](DOCUMENTATION.md#api-documentation) - All API endpoints
- [Phase 1 Summary](API_COMPLETION_SUMMARY.md) - API development details
- [Phase 2 Summary](PHASE2_BACKEND_COMPLETE.md) - Backend integration details
- [Project Status](PROJECT_STATUS.md) - Current project status

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests (`python run_tests.py`)
5. Commit your changes (`git commit -m 'Add your feature'`)
6. Push to the branch (`git push origin feature/your-feature`)
7. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Django](https://www.djangoproject.com/)
- API powered by [Django REST Framework](https://www.django-rest-framework.org/)
- Async tasks with [Celery](https://docs.celeryq.dev/)
- Caching with [Redis](https://redis.io/)
- Documentation with [drf-spectacular](https://github.com/tfranzel/drf-spectacular)

---

## 📞 Support

- **Documentation**: [DOCUMENTATION.md](DOCUMENTATION.md)
- **Issues**: [GitHub Issues](https://github.com/your-username/shop-template/issues)
- **Email**: support@shop-template.com

---

**Version:** 1.0.0  
**Last Updated:** August 11, 2026  
**Status:** ✅ Phase 1 & 2 Complete | ⏳ Phase 3 & 4 Pending
