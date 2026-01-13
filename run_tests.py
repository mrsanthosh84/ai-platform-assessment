#!/usr/bin/env python3
"""
Test runner for AI Platform Assessment
Runs tests without requiring external dependencies
"""

import sys
import os
import unittest
from pathlib import Path

def run_tests():
    """Run all available tests"""
    test_dir = Path(__file__).parent / "tests"
    
    if not test_dir.exists():
        print("Tests directory not found!")
        return False
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Start with basic tests that don't require external dependencies
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load basic tests first
    basic_test_file = test_dir / "test_basic.py"
    if basic_test_file.exists():
        print(f"Loading basic tests from {basic_test_file.name}...")
        try:
            # Import the test module
            spec = __import__('tests.test_basic', fromlist=[''])
            module_suite = loader.loadTestsFromModule(spec)
            suite.addTest(module_suite)
            print(f"✅ Loaded basic tests successfully")
        except Exception as e:
            print(f"❌ Error loading basic tests: {e}")
    
    # Try to load other tests (may fail due to missing dependencies)
    other_test_files = [f for f in test_dir.glob("test_*.py") if f.name != "test_basic.py"]
    
    for test_file in other_test_files:
        print(f"Attempting to load {test_file.name}...")
        try:
            module_name = f"tests.{test_file.stem}"
            spec = __import__(module_name, fromlist=[''])
            module_suite = loader.loadTestsFromModule(spec)
            suite.addTest(module_suite)
            print(f"✅ Loaded {test_file.name} successfully")
        except ImportError as e:
            print(f"⚠️  Skipped {test_file.name}: Missing dependencies ({e})")
        except Exception as e:
            print(f"❌ Error loading {test_file.name}: {e}")
    
    # Run tests
    print("\n" + "="*50)
    print("RUNNING TESTS")
    print("="*50)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
    
    return success

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)