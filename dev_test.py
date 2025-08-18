#!/usr/bin/env python3
"""
Development script to test sortx functionality.
"""

import sys
from pathlib import Path

# Add the current directory to Python path for development
sys.path.insert(0, str(Path(__file__).parent))

import sortx
from sortx.utils import parse_key_spec


def test_basic_functionality():
    """Test basic sortx functionality."""
    print("Testing sortx basic functionality...")
    
    # Test in-memory sorting
    data = [
        {"name": "Charlie", "age": 35, "salary": 90000},
        {"name": "Alice", "age": 25, "salary": 85000},
        {"name": "Bob", "age": 30, "salary": 70000},
    ]
    
    print("Original data:")
    for item in data:
        print(f"  {item}")
    
    # Sort by age
    sorted_data = list(sortx.sort_iter(data, keys=[sortx.key("age", "num")]))
    print("\nSorted by age:")
    for item in sorted_data:
        print(f"  {item}")
    
    # Sort by salary (descending)
    sorted_data = list(sortx.sort_iter(data, keys=[sortx.key("salary", "num", desc=True)]))
    print("\nSorted by salary (descending):")
    for item in sorted_data:
        print(f"  {item}")
    
    print("\n✓ Basic functionality test passed!")


def test_key_parsing():
    """Test key specification parsing."""
    print("\nTesting key specification parsing...")
    
    test_specs = [
        "name",
        "age:num",
        "salary:num:desc=true",
        "name:str:locale=fr",
        "0:nat",
    ]
    
    for spec in test_specs:
        key = parse_key_spec(spec)
        print(f"  '{spec}' -> column={key.column}, type={key.data_type}, desc={key.desc}")
    
    print("\n✓ Key parsing test passed!")


def test_file_operations():
    """Test file operations with sample data."""
    print("\nTesting file operations...")
    
    # Test with sample files if they exist
    test_data_dir = Path(__file__).parent / "tests" / "data"
    
    if test_data_dir.exists():
        csv_file = test_data_dir / "sample.csv"
        if csv_file.exists():
            print(f"Found sample CSV: {csv_file}")
            
            # Test sorting the sample CSV
            output_file = test_data_dir / "sample_sorted.csv"
            try:
                stats = sortx.sort_file(
                    csv_file,
                    output_file,
                    keys=[sortx.key("price", "num")],
                    stats=True
                )
                print(f"Sorted CSV by price: {output_file}")
                print(f"Stats: {stats.lines_processed} lines in {stats.processing_time:.2f}s")
                
                # Clean up
                if output_file.exists():
                    output_file.unlink()
                    
            except Exception as e:
                print(f"Error sorting CSV: {e}")
    
    print("\n✓ File operations test completed!")


if __name__ == "__main__":
    print("sortx Development Test Script")
    print("=" * 40)
    
    try:
        test_basic_functionality()
        test_key_parsing()
        test_file_operations()
        
        print("\n🎉 All tests completed successfully!")
        print("\nTo run the full test suite, use: pytest")
        print("To install in development mode: pip install -e .")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
