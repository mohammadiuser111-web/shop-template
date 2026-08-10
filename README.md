# Shop Template

## معرفی پروژه

**Shop Template** یک قالب (Template) کامل و قابل فروش مجدد برای سایت‌های فروشگاهی است که شامل سه بخش اصلی می‌باشد:

1. **فروشگاه (Store)** — نمایش و فروش محصول
2. **مجله/بلاگ (Magazine)** — تولید محتوا
3. **پنل ادمین (Admin Panel)** — مدیریت کامل سایت

## هدف پروژه

هدف نهایی ساخت یک **Boilerplate/Template حرفه‌ای** است که:
- برای هر کارفرمای جدید فقط با تغییر چند **متغیر پیکربندی** (رنگ، فونت، لوگو، نام برند، دیتابیس) آماده‌ی تحویل شود
- توسعه‌ی پروژه‌های بعدی را از هفته‌ها به روزها کاهش دهد
- ساختار کد آن‌قدر تمیز و مستند باشد که هر توسعه‌دهنده‌ای بتواند به‌راحتی در آن تغییر ایجاد کند

## استک فنی (Tech Stack)

- **Backend:** Django 5.0 + Django REST Framework
- **Frontend:** HTML5 + CSS3 (متغیرمحور با CSS Custom Properties) + JavaScript (Vanilla)
- **Database:** PostgreSQL (پیش‌فرض) با لایه انتزاعی برای پشتیبانی از MySQL/MongoDB
- **Cache/Queue:** Redis (برای کش، سشن، و صف کارهای پس‌زمینه با Celery)
- **Static/Media:** جدا از کد، با پشتیبانی از CDN
- **Deployment:** Docker + Docker Compose، آماده برای Nginx + Gunicorn

## ساختار پوشه‌ها

```
shop-template/
├── config/                      # تنظیمات اصلی پروژه
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
├── apps/
│   ├── core/                    # ابزارهای مشترک
│   ├── accounts/                # ثبت‌نام، ورود، پروفایل
│   ├── products/                # محصولات، دسته‌بندی، برند
│   ├── cart/                    # سبد خرید
│   ├── orders/                  # سفارش‌ها
│   ├── payments/                # درگاه پرداخت
│   ├── shipping/                # روش‌های ارسال
│   ├── inventory/               # موجودی و انبار
│   ├── discounts/                # کد تخفیف و کمپین
│   ├── blog/                    # مجله/بلاگ
│   ├── reviews/                 # نظرات محصول
│   ├── ads/                     # مدیریت تبلیغات
│   ├── notifications/           # اعلان‌ها
│   ├── support/                 # تیکتینگ
│   └── dashboard_admin/         # پنل ادمین سفارشی
├── theme/                       # تمام چیزهای متغیر
│   ├── config.json              # پالت رنگی، فونت، لوگو
│   ├── colors.css
│   ├── fonts/
│   └── logo/
├── static/
│   ├── css/
│   ├── js/
│   └── icons/
├── templates/
│   ├── base.html
│   ├── includes/
│   ├── store/
│   ├── cart/
│   ├── checkout/
│   ├── accounts/
│   ├── blog/
│   ├── admin_panel/
│   └── errors/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── .env.example
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── production.txt
├── manage.py
└── README.md
```

## نصب و اجرا

### پیش‌نیازها

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker و Docker Compose (برای deployment)

### نصب در محیط توسعه

```bash
# Clone پروژه
git clone https://github.com/mohammadiuser111-web/shop-template.git
cd shop-template

# ایجاد محیط مجازی
python -m venv venv
source venv/bin/activate  # در ویندوز: venv\Scripts\activate

# نصب وابستگی‌ها
pip install -r requirements/dev.txt

# تنظیم متغیرهای محیطی
cp docker/.env.example .env
# ویرایش فایل .env با تنظیمات خودتان

# ایجاد و اعمال مایگریشن‌ها
python manage.py migrate

# ایجاد سوپر یوزر
python manage.py createsuperuser

# اجرا کردن سرور توسعه
python manage.py runserver
```

### اجرا در محیط تولید

```bash
# Clone پروژه
git clone https://github.com/mohammadiuser111-web/shop-template.git
cd shop-template

# کپی فایل تنظیمات محیطی
cp docker/.env.example .env
# ویرایش فایل .env

# ساخت و اجرا با Docker
docker-compose -f docker/docker-compose.yml up -d --build
```

## شخصی‌سازی

### تغییر تم (Theme)

برای تغییر ظاهر سایت، کافی است فایل `theme/config.json` را ویرایش کنید:

```json
{
    "name": "نام سایت",
    "slogan": "شعار سایت",
    "logo": "path/to/logo.png",
    "colors": {
        "primary": "#2563eb",
        "secondary": "#7c3aed",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "info": "#3b82f6",
        "light": "#f8fafc",
        "dark": "#1e293b",
        "background": "#ffffff",
        "text": "#1e293b"
    },
    "fonts": {
        "persian": {
            "name": "Vazir",
            "path": "/static/fonts/Vazir.woff2"
        },
        "latin": {
            "name": "Inter",
            "path": "/static/fonts/Inter.woff2"
        }
    }
}
```

### تغییر تنظیمات سایت

می‌توانید تنظیمات کلی سایت را از طریق پنل ادمین یا فایل `apps/core/models.py` تغییر دهید.

### تغییر دیتابیس

برای تغییر دیتابیس، کافی است تنظیمات مربوطه را در فایل `.env` تغییر دهید:

```bash
# PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=shop_template
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# MySQL
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=shop_template
# DB_USER=root
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=3306
```

## ویژگی‌ها

### فروشگاه
- نمایش محصولات با فیلتر پیشرفته
- صفحه جزئیات محصول با گالری تصویر
- سبد خرید با AJAX
- فرآیند تسویه‌حساب چند مرحله‌ای
- درگاه پرداخت با لایه انتزاعی

### مجله/بلاگ
- مدیریت مقالات
- دسته‌بندی و تگ‌ها
- نظرات کاربران
- جستجوی مقالات

### پنل ادمین
- داشبورد با آمار و نمودار
- مدیریت محصولات، سفارش‌ها، مشتریان
- مدیریت بلاگ و نظرات
- مدیریت تبلیغات
- مدیریت کاربران و سطوح دسترسی (RBAC)
- گزارش فعالیت‌ها

### سیستم تبلیغات
- تعریف بنرها و تبلیغات
- جایگاه‌های تبلیغاتی مختلف
- شمارش نمایش و کلیک
- گزارش‌گیری

### کارایی و مقیاس‌پذیری
- کش صفحات با Redis
- بهینه‌سازی کوئری‌ها
- Lazy Loading تصاویر
- فشرده‌سازی فایل‌های استاتیک
- پشتیبانی از Docker و Horizontal Scaling

## تست

```bash
# اجرا کردن تست‌ها
python manage.py test

# اجرا کردن تست‌ها با پوشش کد
pytest --cov=.

# تست بار (Load Test)
locust -f tests/load_test.py
```

## مستندسازی

- [مستندات کامل پروژه](docs/PROJECT_PROMPT.md)
- [گزارش تست](docs/TEST_REPORT.md)

## مشارکت

برای مشارکت در این پروژه، لطفاً:

1. پروژه را Fork کنید
2. یک branch جدید ایجاد کنید (`git checkout -b feature/your-feature`)
3. تغییرات خود را commit کنید (`git commit -am 'Add some feature'`)
4. به branch خود push کنید (`git push origin feature/your-feature`)
5. یک Pull Request ایجاد کنید

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

---

**ساخت: 1403/05/19**
**آخرین بروزرسانی: 1403/05/19**
