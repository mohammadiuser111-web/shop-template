#!/usr/bin/env python
"""
Manage translations
Shop Template - Django E-commerce Template
"""

import os
import sys
import subprocess
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


def extract_translations():
    """Extract translations from source files"""
    print("Extracting translations...")
    
    # Create locale directory if it doesn't exist
    locale_dir = BASE_DIR / 'locale'
    locale_dir.mkdir(exist_ok=True)
    
    # Extract from Python files
    call_command('makemessages', '--all', '--ignore=venv', '--ignore=node_modules')
    
    # Extract from JavaScript files (if using django-js-reverse or similar)
    # call_command('makemessages', '--domain=djangojs', '--all')
    
    print("Translations extracted!")


def update_translations():
    """Update translation files from source files"""
    print("Updating translations...")
    
    # Update from Python files
    call_command('makemessages', '--all', '--ignore=venv', '--ignore=node_modules', '--no-wrap')
    
    print("Translations updated!")


def compile_translations():
    """Compile translation files"""
    print("Compiling translations...")
    
    # Compile all languages
    call_command('compilemessages', '--ignore=venv', '--ignore=node_modules')
    
    print("Translations compiled!")


def create_language(language_code):
    """Create a new language directory"""
    print(f"Creating language directory for {language_code}...")
    
    # Create locale directory if it doesn't exist
    locale_dir = BASE_DIR / 'locale'
    locale_dir.mkdir(exist_ok=True)
    
    # Create language directory
    lang_dir = locale_dir / language_code
    lang_dir.mkdir(exist_ok=True)
    
    # Create LC_MESSAGES directory
    lc_messages_dir = lang_dir / 'LC_MESSAGES'
    lc_messages_dir.mkdir(exist_ok=True)
    
    # Create empty django.po file
    po_file = lc_messages_dir / 'django.po'
    po_file.touch()
    
    print(f"Language directory created: {lang_dir}")


def list_languages():
    """List available languages"""
    print("Available languages:")
    
    locale_dir = BASE_DIR / 'locale'
    if locale_dir.exists():
        for lang_dir in sorted(locale_dir.iterdir()):
            if lang_dir.is_dir():
                print(f"  - {lang_dir.name}")
    else:
        print("  No languages found")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage Django translations')
    parser.add_argument('--extract', action='store_true', help='Extract translations from source files')
    parser.add_argument('--update', action='store_true', help='Update translation files')
    parser.add_argument('--compile', action='store_true', help='Compile translation files')
    parser.add_argument('--all', action='store_true', help='Extract, update, and compile translations')
    parser.add_argument('--create', type=str, metavar='LANGUAGE_CODE', help='Create a new language directory')
    parser.add_argument('--list', action='store_true', help='List available languages')
    
    args = parser.parse_args()
    
    if args.list:
        list_languages()
    elif args.create:
        create_language(args.create)
    elif args.all:
        extract_translations()
        update_translations()
        compile_translations()
    else:
        if args.extract:
            extract_translations()
        if args.update:
            update_translations()
        if args.compile:
            compile_translations()
        if not (args.extract or args.update or args.compile):
            parser.print_help()


if __name__ == '__main__':
    main()
