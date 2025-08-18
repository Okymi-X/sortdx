"""
Integration tests for sortx CLI and file operations.
"""

import tempfile
from pathlib import Path

from sortx import sort_file, key
from sortx.parsers import parse_file, write_file


def test_sort_csv_file():
    """Test sorting a CSV file end-to-end."""
    # Create test CSV data
    csv_data = [
        {"name": "Charlie", "age": "35", "salary": "90000"},
        {"name": "Alice", "age": "25", "salary": "85000"},
        {"name": "Bob", "age": "30", "salary": "70000"},
    ]
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as input_f, \
         tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as output_f:
        
        input_path = Path(input_f.name)
        output_path = Path(output_f.name)
    
    try:
        # Write test data
        write_file(input_path, csv_data, "csv")
        
        # Sort by age (numeric)
        stats = sort_file(
            input_path,
            output_path,
            keys=[key("age", "num")],
            stats=True
        )
        
        # Verify results
        with parse_file(output_path) as reader:
            sorted_data = list(reader)
        
        ages = [int(row["age"]) for row in sorted_data]
        assert ages == [25, 30, 35]
        
        # Check stats
        assert stats.lines_processed == 3
        assert stats.input_file == str(input_path)
        assert stats.output_file == str(output_path)
        
    finally:
        input_path.unlink()
        output_path.unlink()


def test_sort_jsonl_file():
    """Test sorting a JSONL file end-to-end."""
    # Create test JSONL data
    jsonl_data = [
        {"id": 3, "name": "Charlie", "timestamp": "2025-01-15T12:00:00Z"},
        {"id": 1, "name": "Alice", "timestamp": "2025-01-15T10:00:00Z"},
        {"id": 2, "name": "Bob", "timestamp": "2025-01-15T11:00:00Z"},
    ]
    
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as input_f, \
         tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as output_f:
        
        input_path = Path(input_f.name)
        output_path = Path(output_f.name)
    
    try:
        # Write test data
        write_file(input_path, jsonl_data, "jsonl")
        
        # Sort by timestamp (date)
        sort_file(
            input_path,
            output_path,
            keys=[key("timestamp", "date")]
        )
        
        # Verify results
        with parse_file(output_path) as reader:
            sorted_data = list(reader)
        
        names = [row["name"] for row in sorted_data]
        assert names == ["Alice", "Bob", "Charlie"]
        
    finally:
        input_path.unlink()
        output_path.unlink()


def test_sort_with_uniqueness():
    """Test sorting with uniqueness constraint."""
    # Create test data with duplicates
    data = [
        {"id": 1, "name": "Alice", "score": 95},
        {"id": 2, "name": "Bob", "score": 87},
        {"id": 1, "name": "Alice Duplicate", "score": 92},  # Duplicate ID
        {"id": 3, "name": "Charlie", "score": 91},
    ]
    
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as input_f, \
         tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as output_f:
        
        input_path = Path(input_f.name)
        output_path = Path(output_f.name)
    
    try:
        # Write test data
        write_file(input_path, data, "jsonl")
        
        # Sort by score with uniqueness on id
        sort_file(
            input_path,
            output_path,
            keys=[key("score", "num")],
            unique="id"
        )
        
        # Verify results
        with parse_file(output_path) as reader:
            sorted_data = list(reader)
        
        # Should have only 3 items (duplicates removed)
        assert len(sorted_data) == 3
        ids = [row["id"] for row in sorted_data]
        assert len(set(ids)) == 3  # All unique
        
    finally:
        input_path.unlink()
        output_path.unlink()


def test_multi_key_sort():
    """Test multi-key sorting."""
    # Create test data
    data = [
        {"dept": "Engineering", "name": "Charlie", "salary": 90000},
        {"dept": "Engineering", "name": "Alice", "salary": 85000},
        {"dept": "Sales", "name": "Bob", "salary": 70000},
        {"dept": "Sales", "name": "David", "salary": 75000},
    ]
    
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as input_f, \
         tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as output_f:
        
        input_path = Path(input_f.name)
        output_path = Path(output_f.name)
    
    try:
        # Write test data
        write_file(input_path, data, "jsonl")
        
        # Sort by department, then by salary (descending)
        sort_file(
            input_path,
            output_path,
            keys=[
                key("dept", "str"),
                key("salary", "num", desc=True)
            ]
        )
        
        # Verify results
        with parse_file(output_path) as reader:
            sorted_data = list(reader)
        
        # Check order: Engineering (Charlie, Alice), Sales (David, Bob)
        expected_names = ["Charlie", "Alice", "David", "Bob"]
        actual_names = [row["name"] for row in sorted_data]
        assert actual_names == expected_names
        
    finally:
        input_path.unlink()
        output_path.unlink()


def test_natural_sorting():
    """Test natural sorting."""
    # Create test data with filenames
    data = ["file10.txt", "file2.txt", "file1.txt", "file20.txt"]
    
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as input_f, \
         tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as output_f:
        
        input_path = Path(input_f.name)
        output_path = Path(output_f.name)
    
    try:
        # Write test data
        write_file(input_path, data, "txt")
        
        # Sort naturally
        sort_file(
            input_path,
            output_path,
            keys=[key(0, "nat")]  # First column (line content) with natural sort
        )
        
        # Verify results
        with parse_file(output_path) as reader:
            sorted_data = list(reader)
        
        # Natural order should be: file1, file2, file10, file20
        expected = ["file1.txt", "file2.txt", "file10.txt", "file20.txt"]
        assert sorted_data == expected
        
    finally:
        input_path.unlink()
        output_path.unlink()
