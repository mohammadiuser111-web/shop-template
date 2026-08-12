#!/usr/bin/env python
"""
Script to run ads app tests.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')

django.setup()

# Import and run tests
from django.test.utils import get_runner
from django.conf import settings

TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=2, interactive=True, keepdb=False)

# Run all ads tests
failures = test_runner.run_tests(['apps.ads.tests'])

if failures:
    sys.exit(1)
