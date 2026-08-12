#!/usr/bin/env python
"""
Collect and manage static assets
Shop Template - Django E-commerce Template
"""

import os
import sys
import shutil
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Add project directory to path
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_template.settings')
import django
django.setup()

from django.core.management import call_command
from django.conf import settings
from django.contrib.staticfiles import finders


def collect_static():
    """Collect static files"""
    print("Collecting static files...")
    
    # Clear existing static files
    static_root = Path(settings.STATIC_ROOT)
    if static_root.exists():
        print(f"Clearing existing static files from {static_root}...")
        shutil.rmtree(static_root)
    
    # Collect static files
    call_command('collectstatic', '--noinput', '--clear', verbosity=2)
    
    print("Static files collected!")


def compress_static():
    """Compress static files (CSS, JS)"""
    print("Compressing static files...")
    
    try:
        call_command('compress', '--force', verbosity=2)
        print("Static files compressed!")
    except Exception as e:
        print(f"Error compressing static files: {e}")
        print("Make sure django-compressor is installed")


def list_static_files():
    """List all static files"""
    print("Static files:")
    
    for finder in finders.get_finders():
        for path, storage in finder.list([]):
            print(f"  {path}")


def check_static_files():
    """Check if static files are properly configured"""
    print("Checking static files configuration...")
    
    # Check STATIC_URL
    print(f"STATIC_URL: {settings.STATIC_URL}")
    
    # Check STATIC_ROOT
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    
    # Check STATICFILES_DIRS
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    
    # Check STATICFILES_STORAGE
    print(f"STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
    
    # Check if STATIC_ROOT exists
    static_root = Path(settings.STATIC_ROOT)
    if static_root.exists():
        print(f"STATIC_ROOT exists: {static_root}")
        
        # Count files
        file_count = sum(1 for _ in static_root.rglob('*') if _.is_file())
        print(f"Total static files: {file_count}")
    else:
        print(f"STATIC_ROOT does not exist: {static_root}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage static assets')
    parser.add_argument('--collect', action='store_true', help='Collect static files')
    parser.add_argument('--compress', action='store_true', help='Compress static files')
    parser.add_argument('--all', action='store_true', help='Collect and compress static files')
    parser.add_argument('--list', action='store_true', help='List all static files')
    parser.add_argument('--check', action='store_true', help='Check static files configuration')
    
    args = parser.parse_args()
    
    if args.all:
        collect_static()
        compress_static()
    else:
        if args.collect:
            collect_static()
        if args.compress:
            compress_static()
        if args.list:
            list_static_files()
        if args.check:
            check_static_files()
        if not (args.collect or args.compress or args.list or args.check):
            parser.print_help()


if __name__ == '__main__':
    main()
