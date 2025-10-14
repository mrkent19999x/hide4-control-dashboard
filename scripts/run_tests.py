#!/usr/bin/env python3
# scripts/run_tests.py - Test Runner with Coverage Report

"""
Test Runner for Hide4 Control Dashboard

This script runs all unit tests with coverage reporting and generates
HTML coverage reports for easy viewing.

Usage:
    python scripts/run_tests.py [options]

Options:
    --coverage     Generate coverage report
    --html         Generate HTML coverage report
    --verbose      Verbose output
    --parallel     Run tests in parallel
    --module       Run tests for specific module only
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print("Output:", result.stdout)
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("Error:", result.stderr)
            if result.stdout:
                print("Output:", result.stdout)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")

    required_packages = ['pytest', 'pytest-cov']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements-dev.txt")
        return False

    print("✅ All dependencies available")
    return True

def run_tests(args):
    """Run the test suite"""
    print("🧪 Running Hide4 Control Dashboard Test Suite")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        return False

    # Build pytest command
    cmd = ['python', '-m', 'pytest']

    # Add test directory
    test_dir = project_root / 'tests'
    if test_dir.exists():
        cmd.append(str(test_dir))
    else:
        print("❌ Tests directory not found")
        return False

    # Add coverage if requested
    if args.coverage:
        cmd.extend([
            '--cov=client',
            '--cov-report=term-missing',
            '--cov-report=xml:coverage.xml'
        ])

    # Add HTML coverage if requested
    if args.html:
        cmd.extend(['--cov-report=html:htmlcov'])

    # Add verbose if requested
    if args.verbose:
        cmd.append('-v')

    # Add parallel if requested
    if args.parallel:
        cmd.extend(['-n', 'auto'])

    # Add specific module if requested
    if args.module:
        module_test = test_dir / f'test_{args.module}.py'
        if module_test.exists():
            cmd.append(str(module_test))
        else:
            print(f"❌ Test file not found: {module_test}")
            return False

    # Run tests
    success = run_command(cmd, "Running unit tests")

    if success and args.coverage:
        print_coverage_summary()

    if success and args.html:
        print_html_coverage_info()

    return success

def print_coverage_summary():
    """Print coverage summary from XML report"""
    coverage_file = project_root / 'coverage.xml'
    if coverage_file.exists():
        print("\n📊 Coverage Summary:")
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(coverage_file)
            root = tree.getroot()

            # Extract coverage metrics
            line_rate = float(root.get('line-rate', 0)) * 100
            branch_rate = float(root.get('branch-rate', 0)) * 100

            print(f"   Line Coverage: {line_rate:.1f}%")
            print(f"   Branch Coverage: {branch_rate:.1f}%")

            # Show per-file coverage
            packages = root.findall('.//package')
            if packages:
                print("\n   Per-file Coverage:")
                for package in packages:
                    package_name = package.get('name', 'unknown')
                    package_rate = float(package.get('line-rate', 0)) * 100
                    print(f"     {package_name}: {package_rate:.1f}%")

        except Exception as e:
            print(f"   Could not parse coverage report: {e}")

def print_html_coverage_info():
    """Print information about HTML coverage report"""
    htmlcov_dir = project_root / 'htmlcov'
    if htmlcov_dir.exists():
        index_file = htmlcov_dir / 'index.html'
        if index_file.exists():
            print(f"\n📄 HTML Coverage Report: {index_file}")
            print("   Open in browser to view detailed coverage report")

def generate_test_report():
    """Generate a test report summary"""
    print("\n📋 Test Report Summary")
    print("=" * 40)

    # Count test files
    test_dir = project_root / 'tests'
    test_files = list(test_dir.glob('test_*.py'))
    print(f"Test Files: {len(test_files)}")

    # List test files
    for test_file in test_files:
        module_name = test_file.stem.replace('test_', '')
        print(f"  - {module_name}")

    # Check for coverage files
    coverage_files = [
        ('coverage.xml', 'XML Coverage Report'),
        ('htmlcov/index.html', 'HTML Coverage Report')
    ]

    print("\nCoverage Reports:")
    for file_path, description in coverage_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {description}: {full_path}")
        else:
            print(f"  ❌ {description}: Not generated")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run Hide4 Control Dashboard tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--parallel', '-p', action='store_true', help='Run tests in parallel')
    parser.add_argument('--module', '-m', help='Run tests for specific module only')
    parser.add_argument('--report', action='store_true', help='Generate test report')

    args = parser.parse_args()

    if args.report:
        generate_test_report()
        return True

    # Run tests
    success = run_tests(args)

    if success:
        print("\n🎉 All tests passed!")
        generate_test_report()
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
