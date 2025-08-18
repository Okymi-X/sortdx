"""
Test utility functions and classes.
"""

import pytest

from sortx.utils import (
    SortKey,
    SortStats,
    format_size,
    parse_key_spec,
    parse_memory_size,
    validate_sort_keys,
)


def test_sort_key():
    """Test SortKey dataclass."""
    # Basic key
    key = SortKey("name", "str")
    assert key.column == "name"
    assert key.data_type == "str"
    assert key.desc is False
    assert key.locale_name is None
    assert key.options == {}

    # Key with options
    key = SortKey(
        "price", "num", desc=True, locale_name="fr", options={"custom": "value"}
    )
    assert key.column == "price"
    assert key.data_type == "num"
    assert key.desc is True
    assert key.locale_name == "fr"
    assert key.options == {"custom": "value"}


def test_sort_key_post_init():
    """Test SortKey post-init processing."""
    # desc from options
    key = SortKey("name", "str", options={"desc": "true"})
    assert key.desc is True

    # locale from options
    key = SortKey("name", "str", options={"locale": "fr_FR"})
    assert key.locale_name == "fr_FR"


def test_sort_stats():
    """Test SortStats dataclass."""
    stats = SortStats(
        input_file="input.csv",
        output_file="output.csv",
        lines_processed=1000,
        processing_time=2.5,
        input_size=50000,
        output_size=48000,
        external_sort_used=False,
    )

    assert stats.input_file == "input.csv"
    assert stats.lines_processed == 1000
    assert stats.processing_time == 2.5

    # Test string representation
    stats_str = str(stats)
    assert "input.csv" in stats_str
    assert "1,000" in stats_str  # Formatted number
    assert "2.50s" in stats_str  # Formatted time


def test_parse_memory_size():
    """Test memory size parsing."""
    assert parse_memory_size("1024") == 1024
    assert parse_memory_size("1024B") == 1024
    assert parse_memory_size("1K") == 1024
    assert parse_memory_size("1KB") == 1024
    assert parse_memory_size("1M") == 1024 * 1024
    assert parse_memory_size("1G") == 1024 * 1024 * 1024
    assert parse_memory_size("2.5G") == int(2.5 * 1024 * 1024 * 1024)

    # Test case insensitive
    assert parse_memory_size("1m") == 1024 * 1024
    assert parse_memory_size("512mb") == 512 * 1024 * 1024

    # Test with spaces
    assert parse_memory_size(" 1 G ") == 1024 * 1024 * 1024

    # Test invalid formats
    with pytest.raises(ValueError):
        parse_memory_size("invalid")

    with pytest.raises(ValueError):
        parse_memory_size("1X")  # Invalid unit


def test_format_size():
    """Test size formatting."""
    assert format_size(0) == "0B"
    assert format_size(512) == "512B"
    assert format_size(1024) == "1.0K"
    assert format_size(1536) == "1.5K"  # 1.5 * 1024
    assert format_size(1024 * 1024) == "1.0M"
    assert format_size(1024 * 1024 * 1024) == "1.0G"
    assert format_size(int(2.5 * 1024 * 1024 * 1024)) == "2.5G"


def test_parse_key_spec():
    """Test key specification parsing."""
    # Basic key
    key = parse_key_spec("name")
    assert key.column == "name"
    assert key.data_type == "str"

    # Key with type
    key = parse_key_spec("price:num")
    assert key.column == "price"
    assert key.data_type == "num"

    # Key with options
    key = parse_key_spec("name:str:desc=true")
    assert key.column == "name"
    assert key.data_type == "str"
    assert key.options["desc"] is True

    # Key with multiple options
    key = parse_key_spec("name:str:desc=true:locale=fr")
    assert key.column == "name"
    assert key.data_type == "str"
    assert key.options["desc"] is True
    assert key.options["locale"] == "fr"

    # Numeric column index
    key = parse_key_spec("0:num")
    assert key.column == 0
    assert key.data_type == "num"

    # Boolean flag option
    key = parse_key_spec("name:str:case_sensitive")
    assert key.options["case_sensitive"] is True


def test_validate_sort_keys():
    """Test sort key validation."""
    # Valid keys
    keys = [
        SortKey("name", "str"),
        SortKey("age", "num"),
        SortKey("date", "date"),
    ]
    validate_sort_keys(keys)  # Should not raise

    # Invalid data type
    keys = [SortKey("name", "invalid_type")]
    with pytest.raises(ValueError, match="invalid data type"):
        validate_sort_keys(keys)

    # Empty column
    keys = [SortKey("", "str")]
    with pytest.raises(ValueError, match="empty column"):
        validate_sort_keys(keys)

    # Non-SortKey object
    keys = ["not_a_sort_key"]
    with pytest.raises(ValueError, match="not a SortKey object"):
        validate_sort_keys(keys)


def test_parse_key_spec_edge_cases():
    """Test edge cases in key specification parsing."""
    # Empty string should raise
    with pytest.raises(ValueError):
        parse_key_spec("")

    # Numeric values in options
    key = parse_key_spec("col:str:priority=10")
    assert key.options["priority"] == 10

    # Boolean values
    key = parse_key_spec("col:str:flag=false")
    assert key.options["flag"] is False
