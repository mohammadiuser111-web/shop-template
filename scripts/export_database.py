#!/usr/bin/env python
"""
Export database to fixture files
Shop Template - Django E-commerce Template
"""

import os
import sys
import json
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
from django.db import connections


def export_database(output_dir='fixtures', indent=2):
    """
    Export database to fixture files
    
    Args:
        output_dir: Directory to save fixture files
        indent: JSON indentation level
    """
    print(f"Exporting database to {output_dir}...")
    
    # Create output directory if it doesn't exist
    output_path = BASE_DIR / output_dir
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all models
    from django.apps import apps
    
    # Get all app labels
    app_labels = [app.label for app in apps.get_app_configs()]
    
    # Export each app's data
    for app_label in app_labels:
        try:
            print(f"Exporting {app_label}...")
            output_file = str(output_path / f"{app_label}.json")
            call_command('dumpdata', app_label, '--output=' + output_file, '--indent=' + str(indent))
            print(f"  Exported to {output_file}")
        except Exception as e:
            print(f"  Error exporting {app_label}: {e}")
    
    # Export all data
    print("Exporting all data...")
    output_file = str(output_path / "all.json")
    call_command('dumpdata', '--output=' + output_file, '--indent=' + str(indent))
    print(f"  Exported to {output_file}")
    
    print("Database export completed!")


def export_single_model(model_name, output_file, indent=2):
    """
    Export a single model to a fixture file
    
    Args:
        model_name: Model name in format app.Model
        output_file: Output file path
        indent: JSON indentation level
    """
    print(f"Exporting {model_name} to {output_file}...")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_file).parent
    output_path.mkdir(parents=True, exist_ok=True)
    
    call_command('dumpdata', model_name, '--output=' + output_file, '--indent=' + str(indent))
    print(f"  Exported to {output_file}")


def export_custom_query(model_name, query, output_file, indent=2):
    """
    Export custom query results to a fixture file
    
    Args:
        model_name: Model name in format app.Model
        query: Query string (e.g., "id__gt=100")
        output_file: Output file path
        indent: JSON indentation level
    """
    print(f"Exporting {model_name} with query '{query}' to {output_file}...")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_file).parent
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get the model
    from django.apps import apps
    app_label, model_name = model_name.split('.')
    model = apps.get_model(app_label, model_name)
    
    # Get the queryset
    queryset = model.objects.all()
    
    # Apply query
    if query:
        queryset = queryset.filter(**{query: True})
    
    # Export data
    data = []
    for obj in queryset:
        # Convert to serializable format
        from django.core import serializers
        serialized = serializers.serialize('python', [obj])
        data.extend(serialized)
    
    # Write to file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=indent)
    
    print(f"  Exported to {output_file}")


def list_fixtures():
    """List available fixtures"""
    print("Available fixtures:")
    
    fixtures_dir = BASE_DIR / 'fixtures'
    if fixtures_dir.exists():
        for fixture_file in sorted(fixtures_dir.glob('*.json')):
            print(f"  - {fixture_file.name}")
    else:
        print("  No fixtures found")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Export database to fixture files')
    parser.add_argument('--all', action='store_true', help='Export all data')
    parser.add_argument('--app', type=str, metavar='APP_LABEL', help='Export specific app data')
    parser.add_argument('--model', type=str, metavar='MODEL_NAME', help='Export specific model data (format: app.Model)')
    parser.add_argument('--query', type=str, metavar='QUERY', help='Custom query for model export')
    parser.add_argument('--output', type=str, metavar='OUTPUT_FILE', help='Output file path')
    parser.add_argument('--output-dir', type=str, default='fixtures', metavar='OUTPUT_DIR', help='Output directory (default: fixtures)')
    parser.add_argument('--indent', type=int, default=2, metavar='INDENT', help='JSON indentation level (default: 2)')
    parser.add_argument('--list', action='store_true', help='List available fixtures')
    
    args = parser.parse_args()
    
    if args.list:
        list_fixtures()
    elif args.all:
        export_database(args.output_dir, args.indent)
    elif args.app:
        export_single_model(f"{args.app}", args.output or f"{args.app}.json", args.indent)
    elif args.model:
        if args.query:
            export_custom_query(args.model, args.query, args.output or f"{args.model.replace('.', '_')}_query.json", args.indent)
        else:
            export_single_model(args.model, args.output or f"{args.model.replace('.', '_')}.json", args.indent)
    else:
        parser.print_help()


if __name__ == '__main__':
    print("=" * 60)
    print("Shop Template - Database Exporter")
    print("=" * 60)
    print()
    
    main()
    
    print()
    print("=" * 60)
    print("Database export completed!")
    print("=" * 60)
