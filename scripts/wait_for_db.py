#!/usr/bin/env python
"""
Wait for database to be ready
Shop Template - Django E-commerce Template
"""

import os
import sys
import time
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_template.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings
from django.conf import settings

# Import database connection
from django.db import connections
from django.db.utils import OperationalError


def wait_for_db(timeout=60, interval=1):
    """
    Wait for database to be ready
    
    Args:
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try to connect to the database
            connection = connections['default']
            connection.cursor()
            print("Database is ready!")
            return True
        except OperationalError as e:
            print(f"Database not ready yet: {e}")
            print(f"Retrying in {interval} second(s)...")
            time.sleep(interval)
    
    print(f"Timeout waiting for database after {timeout} seconds")
    return False


if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='Wait for database to be ready')
    parser.add_argument('--timeout', type=int, default=60, help='Maximum time to wait in seconds')
    parser.add_argument('--interval', type=int, default=1, help='Time between checks in seconds')
    
    args = parser.parse_args()
    
    # Wait for database
    success = wait_for_db(timeout=args.timeout, interval=args.interval)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
