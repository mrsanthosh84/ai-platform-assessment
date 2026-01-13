#!/usr/bin/env python3
"""
Simple test validation for AI Platform Assessment
Validates test structure and basic functionality
"""

import os
import sys
from pathlib import Path

def validate_test_structure():
    """Validate that test files are properly structured"""
    test_dir = Path(__file__).parent / "tests"
    
    if not test_dir.exists():
        print("❌ Tests directory not found")
        return False
    
    print("✅ Tests directory exists")
    
    # Check for required test files
    required_files = [
        "test_chat.py",
        "test_rag_simple.py", 
        "test_planning_agent.py",
        "test_code_assistant.py",
        "test_dashboard_simple.py",
        "test_integration.py",
        "test_basic.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not (test_dir / file).exists():
            missing_files.append(file)
        else:
            print(f"✅ {file} exists")
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False
    
    # Check test file content
    for test_file in required_files:
        file_path = test_dir / test_file
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Basic checks
            if "import pytest" not in content and "import unittest" not in content:
                print(f"❌ {test_file} missing test framework import")
                return False
            
            if "def test_" not in content and "class Test" not in content:
                print(f"❌ {test_file} missing test functions/classes")
                return False
                
            print(f"✅ {test_file} has valid test structure")
            
        except Exception as e:
            print(f"❌ Error reading {test_file}: {e}")
            return False
    
    # Check configuration files
    config_files = ["pytest.ini", "conftest.py"]
    for config_file in config_files:
        if (test_dir.parent / config_file).exists():
            print(f"✅ {config_file} exists")
        else:
            print(f"⚠️  {config_file} not found (optional)")
    
    return True

def check_imports():
    """Check that main modules can be imported"""
    sys.path.insert(0, str(Path(__file__).parent))
    
    modules = [
        "chat",
        "rag_system", 
        "planning_agent",
        "code_assistant",
        "dashboard"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} can be imported")
        except ImportError as e:
            print(f"❌ Cannot import {module}: {e}")
            return False
        except Exception as e:
            print(f"⚠️  {module} import warning: {e}")
    
    return True

def main():
    """Main validation function"""
    print("🧪 AI Platform Test Validation")
    print("=" * 40)
    
    structure_ok = validate_test_structure()
    imports_ok = check_imports()
    
    print("\n" + "=" * 40)
    if structure_ok:
        print("✅ Test structure validation passed!")
        print("\nTo run tests:")
        print("  python3 run_tests.py         # Runs available tests")
        print("  python3 tests/test_basic.py  # Basic tests only")
        print("\nNote: Some tests require dependencies from requirements.txt")
        print("Install with: pip3 install -r requirements.txt")
        return True
    else:
        print("❌ Test structure validation failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)