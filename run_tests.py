#!/usr/bin/env python
"""
Run tests for Django Shop Template.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py core         # Run tests for specific app
    python run_tests.py --coverage   # Run tests with coverage
    python run_tests.py --verbose    # Run tests with verbose output
"""
import os
import sys
import argparse
import subprocess


def run_tests(app=None, coverage=False, verbose=False, markers=None):
    """Run pytest with specified options."""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    
    # Build pytest command
    cmd = ['pytest']
    
    if verbose:
        cmd.extend(['-v', '-s'])
    
    if coverage:
        cmd.extend(['--cov=apps', '--cov=config', '--cov-report=term-missing'])
    
    if markers:
        cmd.extend(['-m', markers])
    
    if app:
        cmd.extend([f'apps/{app}/tests/'])
    else:
        cmd.extend(['apps/'])
    
    # Run pytest
    print(f"Running tests: {' '.join(cmd)}")
    print("-" * 80)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run tests for Django Shop Template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_tests.py                     Run all tests
    python run_tests.py core               Run tests for core app
    python run_tests.py --coverage         Run tests with coverage
    python run_tests.py --verbose          Run tests with verbose output
    python run_tests.py --markers api      Run only API tests
        """
    )
    
    parser.add_argument(
        'app',
        nargs='?',
        default=None,
        help='Specific app to test (e.g., core, accounts, products)'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Run tests with coverage'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Run tests with verbose output'
    )
    
    parser.add_argument(
        '--markers', '-m',
        default=None,
        help='Run tests with specific markers (e.g., api, unit, integration)'
    )
    
    args = parser.parse_args()
    
    # Run tests
    exit_code = run_tests(
        app=args.app,
        coverage=args.coverage,
        verbose=args.verbose,
        markers=args.markers
    )
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
