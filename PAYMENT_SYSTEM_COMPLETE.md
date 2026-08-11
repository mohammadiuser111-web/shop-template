# سیستم پرداخت - تکمیل شد ✅

## خلاصه

سیستم پرداخت کامل پروژه shop-template با موفقیت پیاده‌سازی شد. این سیستم از درگاه‌های پرداخت ایرانی پشتیبانی می‌کند و شامل تمام اجزای مورد نیاز برای پردازش پرداخت‌های آنلاین است.

## فایل‌های ایجاد شده

### اپ payments

1. **`apps/payments/admin.py`**
   - ModelAdmin برای همه مدل‌ها (PaymentGateway, Transaction, Wallet, WalletTransaction)
   - مدیریت درگاه‌های پرداخت
   - مدیریت تراکنش‌ها
   - مدیریت کیف پول کاربران
   - اقدامات گروهی (تایید، لغو، ناموفق کردن)

2. **`apps/payments/urls.py`**
   - مسیریابی کامل برای سیستم پرداخت
   - انتخاب درگاه پرداخت
   - پردازش پرداخت
   - تایید پرداخت
   - callback برای درگاه‌ها
   - تاریخچه پرداخت‌ها
   - مدیریت کیف پول
   - وب‌هوک‌ها

3. **`apps/payments/forms.py`**
   - PaymentGatewayForm
   - WalletDepositForm
   - WalletWithdrawForm
   - PaymentForm
   - RefundForm
   - PaymentSearchForm

4. **`apps/payments/services.py`**
   - کلاس پایه PaymentGatewayBase
   - ZarinpalGateway
   - IDPayGateway
   - PayIRGateway
   - NextpayGateway
   - PaymentService (کلاس اصلی مدیریت پرداخت‌ها)

5. **`apps/payments/views.py`** (آپدیت شد)
   - ویوهای پردازش پرداخت
   - ویوهای callback
   - ویوهای مدیریت کیف پول
   - ویوهای تاریخچه پرداخت‌ها
   - ویوهای AJAX

6. **`apps/payments/models.py`** (قبلاً ایجاد شده بود)
   - PaymentGateway
   - Transaction
   - Wallet
   - WalletTransaction

### تمپلیت‌ها

7. **`templates/payments/payment_gateway.html`** (قبلاً وجود داشت)
8. **`templates/payments/payment_success.html`** - صفحه موفقیت پرداخت
9. **`templates/payments/payment_failed.html`** - صفحه شکست پرداخت
10. **`templates/payments/payment_history.html`** - تاریخچه پرداخت‌ها
11. **`templates/payments/payment_detail.html`** - جزئیات تراکنش
12. **`templates/payments/receipt.html`** - رسید پرداخت
13. **`templates/payments/wallet.html`** - کیف پول کاربر
14. **`templates/payments/wallet_transactions.html`** - تاریخچه تراکنش‌های کیف پول

### تنظیمات

15. **`config/settings/base.py`** (آپدیت شد)
    - اضافه شدن SITE_URL
    - تنظیمات کامل درگاه‌ها (Zarinpal, IDPay, Pay.ir, NextPay)

16. **`apps/payments/apps.py`** (آپدیت شد)
    - ثبت سرویس‌ها

17. **`apps/payments/__init__.py`** (آپدیت شد)
    - تنظیم default_app_config

## ویژگی‌ها

### درگاه‌های پرداخت
✅ **Zarinpal** - زرین پال
✅ **IDPay** - آی دی پی
✅ **Pay.ir** - پی آی آر
✅ **NextPay** - نکست پی

### ویژگی‌های اصلی

#### پردازش پرداخت
- انتخاب درگاه پرداخت
- ایجاد تراکنش خودکار
- هدایت به درگاه پرداخت
- تایید پرداخت از callback
- به‌روزرسانی خودکار سفارش
- مدیریت خطاهای پرداخت

#### کیف پول
- افزایش موجودی
- برداشت از موجودی
- تاریخچه تراکنش‌ها
- نمایش موجودی فعلی
- محدودیت برداشت بر اساس موجودی

#### مدیریت ادمین
- مدیریت درگاه‌های پرداخت
- فعال/غیرفعال کردن درگاه‌ها
- تنظیمات درگاه‌ها
- مشاهده همه تراکنش‌ها
- فیلتر و جستجوی تراکنش‌ها

#### تاریخچه و گزارش‌ها
- تاریخچه پرداخت‌ها
- فیلتر بر اساس وضعیت
- فیلتر بر اساس درگاه
- جزئیات کامل هر تراکنش
- رسید چاپی

#### امنیت
- تایید callback از درگاه
- ذخیره اطلاعات کامل تراکنش
- مدیریت خطاهای پرداخت
- وب‌هوک برای درگاه‌ها

## API Endpoints

### پردازش پرداخت
- `GET /payments/select/` - انتخاب درگاه پرداخت
- `POST /payments/process/<gateway_type>/` - پردازش پرداخت
- `GET /payments/verify/<gateway_type>/` - تایید پرداخت

### Callback
- `GET /payments/callback/zarinpal/` - callback زرین پال
- `GET /payments/callback/idpay/` - callback آی دی پی
- `GET /payments/callback/payir/` - callback پی آی آر
- `GET /payments/callback/nextpay/` - callback نکست پی

### کیف پول
- `GET /payments/wallet/` - صفحه کیف پول
- `POST /payments/wallet/deposit/` - افزایش موجودی
- `POST /payments/wallet/withdraw/` - برداشت از موجودی
- `GET /payments/wallet/transactions/` - تاریخچه تراکنش‌ها

### تاریخچه
- `GET /payments/history/` - تاریخچه پرداخت‌ها
- `GET /payments/history/<transaction_id>/` - جزئیات تراکنش
- `GET /payments/receipt/<transaction_id>/` - رسید پرداخت

### وب‌هوک
- `POST /payments/webhook/<gateway_type>/` - وب‌هوک درگاه

### AJAX
- `GET /payments/api/wallet-balance/` - دریافت موجودی
- `GET /payments/api/payment-status/<transaction_id>/` - وضعیت پرداخت
- `GET /payments/api/gateways/` - لیست درگاه‌ها
- `POST /payments/api/create-transaction/` - ایجاد تراکنش

## تنظیمات محیطی

```bash
# Zarinpal
ZARINPAL_MERCHANT_ID=your_merchant_id
ZARINPAL_SANDBOX=True

# IDPay
IDPAY_API_KEY=your_api_key
IDPAY_SANDBOX=True

# Pay.ir
PAYIR_API_KEY=your_api_key
PAYIR_SANDBOX=True

# NextPay
NEXTPAY_API_KEY=your_api_key
NEXTPAY_SANDBOX=True

# Site URL
SITE_URL=http://localhost:8000
```

## نحوه استفاده

### ۱. تنظیم درگاه پرداخت

```python
# در ادمین Django
# به آدرس /admin/payments/paymentgateway/ بروید
# درگاه جدید ایجاد کنید
# نوع درگاه را انتخاب کنید
# تنظیمات مربوطه را وارد کنید
```

### ۲. پردازش پرداخت

```python
from apps.payments.services import PaymentService

# ایجاد تراکنش
transaction, result = PaymentService.create_payment(
    order=order,
    user=user,
    gateway_type='zarinpal',
    amount=order.total_amount,
    currency='IRR',
    description=f'پرداخت سفارش #{order.code}'
)

# پردازش پرداخت
redirect_url, result = PaymentService.process_payment(transaction, 'zarinpal')
```

### ۳. تایید پرداخت

```python
# در ویو callback
transaction, result = PaymentService.verify_payment(
    'zarinpal',
    {'Authority': authority, 'Status': status}
)

if result['success']:
    # پرداخت موفق بود
    order.status = 'paid'
    order.save()
```

## مدل‌های داده

### PaymentGateway
- `name` - نام داخلی
- `gateway_type` - نوع درگاه (zarinpal, idpay, payir, nextpay)
- `is_active` - فعال/غیرفعال
- `config` - تنظیمات JSON
- `title` - عنوان نمایشی
- `description` - توضیحات
- `logo` - لوگو
- `sort_order` - ترتیب نمایش

### Transaction
- `transaction_id` - شناسه تراکنش
- `user` - کاربر
- `order` - سفارش مربوطه
- `gateway` - درگاه پرداخت
- `amount` - مبلغ
- `currency` - ارز
- `status` - وضعیت (pending, success, failed, cancelled, refunded)
- `transaction_type` - نوع تراکنش (purchase, refund, deposit, withdrawal)
- `gateway_reference` - کد پیگیری درگاه
- `gateway_response` - پاسخ درگاه
- `customer_name` - نام مشتری
- `customer_email` - ایمیل مشتری
- `customer_phone` - تلفن مشتری
- `error_code` - کد خطا
- `error_message` - پیام خطا
- `completed_at` - تاریخ تکمیل

### Wallet
- `user` - کاربر
- `balance` - موجودی

### WalletTransaction
- `wallet` - کیف پول
- `amount` - مبلغ
- `transaction_type` - نوع (deposit, withdrawal, refund)
- `balance_after` - موجودی پس از تراکنش
- `description` - توضیحات
- `transaction` - تراکنش مربوطه

## Git Commit

```bash
commit da7d2ec
Complete payment system implementation
- Add admin.py with ModelAdmin for all payment models
- Add urls.py with comprehensive payment routes
- Add forms.py with all payment forms
- Add services.py with gateway integrations (Zarinpal, IDPay, Pay.ir, NextPay)
- Update views.py with new payment processing logic
- Add payment templates: success, failed, history, detail, receipt, wallet, wallet_transactions
- Update apps.py and __init__.py
- Update settings with SITE_URL and all gateway configurations
```

## وضعیت پروژه

✅ **تکمیل شد**: سیستم پرداخت
✅ **تکمیل شد**: سفارشی‌سازی پنل مدیریت
⏳ **در حال انجام**: سیستم تبلیغات
⏳ **در انتظار**: تست‌ها، بهینه‌سازی‌ها

## لینک‌ها

- **مخزن GitHub**: https://github.com/mohammadiuser111-web/shop-template
- **Commit**: https://github.com/mohammadiuser111-web/shop-template/commit/da7d2ec
- **فایل مستندات**: [PAYMENT_SYSTEM_COMPLETE.md](/home/user/shop-template/PAYMENT_SYSTEM_COMPLETE.md)

---

**تاریخ تکمیل**: ۱۴۰۵/۰۵/۲۰ (۲۰۲۶-۰۸-۱۱)
