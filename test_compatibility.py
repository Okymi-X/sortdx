#!/usr/bin/env python3
"""
Script de test pour vérifier la compatibilité multi-version
"""

import sys
import importlib


def test_imports():
    """Test basic imports"""
    try:
        import sortx
        import sortx.cli
        import sortx.core
        import sortx.parsers
        import sortx.utils
        print(f"✓ All imports successful on Python {sys.version}")
        return True
    except Exception as e:
        print(f"✗ Import failed on Python {sys.version}: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality"""
    try:
        from sortx.core import sort_iter, key
        from sortx.utils import parse_key_spec
        
        # Test parse_key_spec
        sort_key = parse_key_spec("age:num")
        assert sort_key.column == "age"
        assert sort_key.data_type == "num"
        
        # Test basic sorting
        data = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
        sorted_data = list(sort_iter(data, [sort_key]))
        assert sorted_data[0]["age"] == 25
        assert sorted_data[1]["age"] == 30
        
        print(f"✓ Basic functionality works on Python {sys.version}")
        return True
    except Exception as e:
        print(f"✗ Basic functionality failed on Python {sys.version}: {e}")
        return False


def main():
    """Main test function"""
    print(f"Testing sortx on Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    success = True
    success &= test_imports()
    success &= test_basic_functionality()
    
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
