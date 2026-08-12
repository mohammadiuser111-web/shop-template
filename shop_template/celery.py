"""
Celery configuration for Shop Template.

This module configures Celery for asynchronous task processing.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_template.settings')

# Create Celery app
app = Celery('shop_template')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# ============================================
# Celery Beat Schedule
# ============================================

app.conf.beat_schedule = {
    # Clean up expired sessions
    'cleanup-expired-sessions': {
        'task': 'core.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=3, minute=0),  # Every day at 3 AM
    },
    
    # Clean up temporary files
    'cleanup-temporary-files': {
        'task': 'core.tasks.cleanup_temporary_files',
        'schedule': crontab(hour=2, minute=0),  # Every day at 2 AM
    },
    
    # Send abandoned cart reminders
    'send-abandoned-cart-reminders': {
        'task': 'orders.tasks.send_abandoned_cart_reminders',
        'schedule': crontab(hour=10, minute=0),  # Every day at 10 AM
    },
    
    # Send newsletters
    'send-newsletters': {
        'task': 'newsletter.tasks.send_scheduled_newsletters',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    
    # Update product statistics
    'update-product-statistics': {
        'task': 'products.tasks.update_product_statistics',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    
    # Clean up old logs
    'cleanup-old-logs': {
        'task': 'core.tasks.cleanup_old_logs',
        'schedule': crontab(hour=1, minute=0),  # Every day at 1 AM
    },
    
    # Generate sitemap
    'generate-sitemap': {
        'task': 'core.tasks.generate_sitemap',
        'schedule': crontab(minute=0, hour='*/12'),  # Every 12 hours
    },
    
    # Check for low stock products
    'check-low-stock-products': {
        'task': 'products.tasks.check_low_stock_products',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
    },
    
    # Send order status notifications
    'send-order-status-notifications': {
        'task': 'orders.tasks.send_order_status_notifications',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    
    # Clean up expired coupons
    'cleanup-expired-coupons': {
        'task': 'coupons.tasks.cleanup_expired_coupons',
        'schedule': crontab(hour=4, minute=0),  # Every day at 4 AM
    },
    
    # Update cache
    'update-cache': {
        'task': 'core.tasks.update_cache',
        'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours
    },
    
    # Backup database (daily)
    'backup-database': {
        'task': 'core.tasks.backup_database',
        'schedule': crontab(hour=0, minute=0),  # Every day at midnight
    },
    
    # Send daily sales report
    'send-daily-sales-report': {
        'task': 'orders.tasks.send_daily_sales_report',
        'schedule': crontab(hour=23, minute=59),  # Every day at 11:59 PM
    },
    
    # Send weekly performance report
    'send-weekly-performance-report': {
        'task': 'core.tasks.send_weekly_performance_report',
        'schedule': crontab(day_of_week=0, hour=23, minute=59),  # Every Sunday at 11:59 PM
    },
    
    # Send monthly newsletter
    'send-monthly-newsletter': {
        'task': 'newsletter.tasks.send_monthly_newsletter',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # Every 1st of the month at 9 AM
    },
}

# ============================================
# Celery Configuration
# ============================================

# Task routes
app.conf.task_routes = {
    'core.tasks.*': {'queue': 'core'},
    'users.tasks.*': {'queue': 'users'},
    'products.tasks.*': {'queue': 'products'},
    'orders.tasks.*': {'queue': 'orders'},
    'payments.tasks.*': {'queue': 'payments'},
    'shipping.tasks.*': {'queue': 'shipping'},
    'newsletter.tasks.*': {'queue': 'newsletter'},
    'reviews.tasks.*': {'queue': 'reviews'},
    'wishlist.tasks.*': {'queue': 'wishlist'},
    'compare.tasks.*': {'queue': 'compare'},
    'coupons.tasks.*': {'queue': 'coupons'},
    'notifications.tasks.*': {'queue': 'notifications'},
    'api.tasks.*': {'queue': 'api'},
}

# Queue configuration
app.conf.task_queues = (
    Queue('core', routing_key='core'),
    Queue('users', routing_key='users'),
    Queue('products', routing_key='products'),
    Queue('orders', routing_key='orders'),
    Queue('payments', routing_key='payments'),
    Queue('shipping', routing_key='shipping'),
    Queue('newsletter', routing_key='newsletter'),
    Queue('reviews', routing_key='reviews'),
    Queue('wishlist', routing_key='wishlist'),
    Queue('compare', routing_key='compare'),
    Queue('coupons', routing_key='coupons'),
    Queue('notifications', routing_key='notifications'),
    Queue('api', routing_key='api'),
)

# Task default queue
app.conf.task_default_queue = 'default'
app.conf.task_default_routing_key = 'default'

# ============================================
# Task Timeouts
# ============================================

# Default timeout for all tasks (in seconds)
app.conf.task_time_limit = 3600  # 1 hour
app.conf.task_soft_time_limit = 1800  # 30 minutes

# Task-specific timeouts
app.conf.task_time_limits = {
    'core.tasks.backup_database': 7200,  # 2 hours
    'core.tasks.generate_sitemap': 3600,  # 1 hour
    'products.tasks.update_product_statistics': 1800,  # 30 minutes
}

# ============================================
# Task Retry
# ============================================

# Default retry settings
app.conf.task_max_retries = 3
app.conf.task_default_retry_delay = 60  # 1 minute
app.conf.task_retry_backoff = True
app.conf.task_retry_backoff_max = 600  # 10 minutes

# Task-specific retry settings
app.conf.task_retry_delays = {
    'core.tasks.backup_database': [300, 600, 1200],  # 5min, 10min, 20min
    'orders.tasks.send_order_status_notifications': [60, 120, 300],  # 1min, 2min, 5min
}

# ============================================
# Rate Limits
# ============================================

# Rate limit for tasks
app.conf.worker_max_tasks_per_child = 1000
app.conf.worker_max_memory_per_child = 300000  # 300MB
app.conf.worker_prefetch_multiplier = 4

# ============================================
# Result Backend
# ============================================

# Result expiration
app.conf.result_expires = 3600  # 1 hour
app.conf.result_extended = True
app.conf.result_compression = True
app.conf.result_serializer = 'json'

# ============================================
# Worker Settings
# ============================================

# Worker concurrency
app.conf.worker_concurrency = 4
app.conf.worker_log_color = True
app.conf.worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
app.conf.worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s'

# ============================================
# Security
# ============================================

# Task message serialization
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.timezone = 'UTC'
app.conf.enable_utc = True

# ============================================
# Monitoring
# ============================================

# Flower monitoring (optional)
app.conf.flower_port = 5555
app.conf.flower_url_prefix = '/flower'
app.conf.flower_basic_auth = [('admin', 'admin')]  # Change in production

# ============================================
# Custom Task Classes
# ============================================


class DebugTask(Celery.Task):
    """Task class with debug logging"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super().on_failure(exc, task_id, args, kwargs, einfo)
        print(f'Task {task_id} failed: {exc}')
    
    def on_success(self, retval, task_id, args, kwargs):
        super().on_success(retval, task_id, args, kwargs)
        print(f'Task {task_id} succeeded')
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        super().on_retry(exc, task_id, args, kwargs, einfo)
        print(f'Task {task_id} retrying: {exc}')


# Register custom task class
app.conf.task_default_base = DebugTask

# ============================================
# Task Decorators
# ============================================


# Example task decorator for high priority tasks
def high_priority(task):
    """Decorator for high priority tasks"""
    task.options['queue'] = 'high_priority'
    task.options['routing_key'] = 'high_priority'
    return task


# Example task decorator for low priority tasks
def low_priority(task):
    """Decorator for low priority tasks"""
    task.options['queue'] = 'low_priority'
    task.options['routing_key'] = 'low_priority'
    return task


# ============================================
# Task Utilities
# ============================================


def get_task_logger(name='celery'):
    """Get logger for Celery tasks"""
    import logging
    return logging.getLogger(f'{name}.tasks')


def retry_on_failure(exceptions, max_retries=3, delay=60):
    """Decorator to retry task on specific exceptions"""
    from functools import wraps
    
    def decorator(task):
        @wraps(task)
        def wrapper(*args, **kwargs):
            try:
                return task(*args, **kwargs)
            except exceptions as e:
                raise task.retry(exc=e, countdown=delay)
        return wrapper
    return decorator


# ============================================
# Export
# ============================================

__all__ = ['app', 'DebugTask', 'high_priority', 'low_priority', 'get_task_logger', 'retry_on_failure']
