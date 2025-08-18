"""
Test CLI functionality - minimal version.
"""

from sortdx.cli import basic_sort


def test_basic_sort_functionality():
    """Test basic sort without full CLI."""
    # Test data
    data = [
        {"name": "Charlie", "age": 35},
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
    ]

    # Mock args
    class MockArgs:
        keys = ["age:num"]
        reverse = False
        unique = None
        output = None
        format = None
        delimiter = None

    args = MockArgs()

    # Should sort by age
    sorted_data = basic_sort(data, args)
    ages = [item["age"] for item in sorted_data]
    assert ages == [25, 30, 35]


def test_basic_sort_reverse():
    """Test reverse sorting."""
    data = [{"value": i} for i in [1, 3, 2, 5, 4]]

    class MockArgs:
        keys = ["value:num"]
        reverse = True
        unique = None
        output = None
        format = None
        delimiter = None

    args = MockArgs()

    sorted_data = basic_sort(data, args)
    values = [item["value"] for item in sorted_data]
    assert values == [5, 4, 3, 2, 1]


def test_basic_sort_string_keys():
    """Test string sorting."""
    data = [
        {"name": "Charlie"},
        {"name": "Alice"},
        {"name": "Bob"},
    ]

    class MockArgs:
        keys = ["name:str"]
        reverse = False
        unique = None
        output = None
        format = None
        delimiter = None

    args = MockArgs()

    sorted_data = basic_sort(data, args)
    names = [item["name"] for item in sorted_data]
    assert names == ["Alice", "Bob", "Charlie"]
