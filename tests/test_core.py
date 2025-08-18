"""
Test core sorting functionality.
"""

from sortx.core import key, sort_iter, _extract_value, _convert_value


def test_key_creation():
    """Test SortKey creation with key() function."""
    # Basic key
    k = key("name", "str")
    assert k.column == "name"
    assert k.data_type == "str"
    assert k.desc is False

    # Key with options
    k = key("price", "num", desc=True, locale_name="fr_FR")
    assert k.column == "price"
    assert k.data_type == "num"
    assert k.desc is True
    assert k.locale_name == "fr_FR"


def test_extract_value():
    """Test value extraction from different data structures."""
    # Dictionary
    item = {"name": "Alice", "age": 30}
    assert _extract_value(item, "name") == "Alice"
    assert _extract_value(item, "age") == 30
    assert _extract_value(item, "missing") == ""

    # List/tuple
    item = ["Alice", 30, "Engineer"]
    assert _extract_value(item, 0) == "Alice"
    assert _extract_value(item, 1) == 30
    assert _extract_value(item, 5) == ""  # Out of bounds

    # String
    item = "test_string"
    assert _extract_value(item, "any") == "test_string"


def test_convert_value():
    """Test value conversion for different data types."""
    # Numeric conversion
    assert _convert_value("42", "num") == 42
    assert _convert_value("3.14", "num") == 3.14

    # String conversion
    assert _convert_value(123, "str") == "123"
    assert _convert_value("hello", "str") == "hello"

    # Empty values
    assert _convert_value("", "str") == ""
    assert _convert_value(None, "str") == ""


def test_sort_iter_basic():
    """Test basic in-memory sorting."""
    data = [
        {"name": "Charlie", "age": 35},
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
    ]

    # Sort by age
    sorted_data = list(sort_iter(data, keys=[key("age", "num")]))
    ages = [item["age"] for item in sorted_data]
    assert ages == [25, 30, 35]

    # Sort by name
    sorted_data = list(sort_iter(data, keys=[key("name", "str")]))
    names = [item["name"] for item in sorted_data]
    assert names == ["Alice", "Bob", "Charlie"]


def test_sort_iter_reverse():
    """Test reverse sorting."""
    data = [{"value": i} for i in [1, 3, 2, 5, 4]]

    sorted_data = list(sort_iter(data, keys=[key("value", "num")], reverse=True))

    values = [item["value"] for item in sorted_data]
    assert values == [5, 4, 3, 2, 1]


def test_sort_iter_list_data():
    """Test sorting list data."""
    data = [
        [3, "Charlie"],
        [1, "Alice"],
        [2, "Bob"],
    ]

    # Sort by first column (index 0)
    sorted_data = list(sort_iter(data, keys=[key(0, "num")]))

    first_values = [item[0] for item in sorted_data]
    assert first_values == [1, 2, 3]

    # Sort by second column (index 1)
    sorted_data = list(sort_iter(data, keys=[key(1, "str")]))

    second_values = [item[1] for item in sorted_data]
    assert second_values == ["Alice", "Bob", "Charlie"]


def test_sort_iter_empty_data():
    """Test sorting empty data."""
    data = []
    sorted_data = list(sort_iter(data, keys=[key("name", "str")]))
    assert sorted_data == []
