"""
Integration tests for sortx - simplified version.
"""

import tempfile
from pathlib import Path

from sortx import key, sort_file
from sortx.parsers import parse_file


def test_sort_csv_file():
    """Test sorting a CSV file end-to-end."""
    # Create test CSV data
    csv_content = """name,age,salary
Charlie,35,90000
Alice,25,85000
Bob,30,70000"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_f:
        input_f.write(csv_content)
        input_path = Path(input_f.name)
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as output_f:
        output_path = Path(output_f.name)
    
    try:
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
    """Test sorting a JSONL file."""
    # Create test JSONL data
    jsonl_content = '''{"name": "Charlie", "age": 35}
{"name": "Alice", "age": 25}
{"name": "Bob", "age": 30}'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as input_f:
        input_f.write(jsonl_content)
        input_path = Path(input_f.name)
    
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as output_f:
        output_path = Path(output_f.name)
    
    try:
        # Sort by name (string)
        sort_file(
            input_path,
            output_path,
            keys=[key("name", "str")]
        )
        
        # Verify results
        with parse_file(output_path) as reader:
            sorted_data = list(reader)
        
        names = [row["name"] for row in sorted_data]
        assert names == ["Alice", "Bob", "Charlie"]
        
    finally:
        input_path.unlink()
        output_path.unlink()


def test_sort_text_file():
    """Test sorting a text file."""
    # Create test text data
    text_content = """zebra
apple
banana
cherry"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as input_f:
        input_f.write(text_content)
        input_path = Path(input_f.name)
    
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as output_f:
        output_path = Path(output_f.name)
    
    try:
        # Sort text lines
        sort_file(
            input_path,
            output_path,
            keys=[key(None, "str")]  # Sort lines as strings
        )
        
        # Verify results
        with parse_file(output_path) as reader:
            sorted_data = list(reader)
        
        assert sorted_data == ["apple", "banana", "cherry", "zebra"]
        
    finally:
        input_path.unlink()
        output_path.unlink()
