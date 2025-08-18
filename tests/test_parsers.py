"""
Test file parsing functionality - simplified version.
"""

import tempfile
from pathlib import Path

from sortx.parsers import (
    CSVReader,
    JSONLReader,
    TextReader,
    detect_format,
    detect_csv_delimiter,
    parse_file,
    write_file,
)


def test_detect_format():
    """Test file format detection."""
    assert detect_format("data.csv") == "csv"
    assert detect_format("data.tsv") == "tsv"
    assert detect_format("data.tab") == "tsv"
    assert detect_format("data.jsonl") == "jsonl"
    assert detect_format("data.ndjson") == "jsonl"
    assert detect_format("data.json") == "jsonl"
    assert detect_format("data.txt") == "txt"
    assert detect_format("unknown.xyz") == "txt"


def test_csv_reader():
    """Test CSV file reading."""
    # Create temporary CSV file
    csv_content = """name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Chicago"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file = Path(f.name)
    
    try:
        # Test reading
        with CSVReader(csv_file) as reader:
            rows = list(reader)
            assert len(rows) == 3
            assert rows[0] == {"name": "Alice", "age": "25", "city": "New York"}
            assert rows[1] == {"name": "Bob", "age": "30", "city": "San Francisco"}
            assert rows[2] == {"name": "Charlie", "age": "35", "city": "Chicago"}
    finally:
        csv_file.unlink()


def test_jsonl_reader():
    """Test JSONL file reading."""
    # Create temporary JSONL file
    jsonl_content = '''{"name": "Alice", "age": 25, "city": "New York"}
{"name": "Bob", "age": 30, "city": "San Francisco"}
{"name": "Charlie", "age": 35, "city": "Chicago"}'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write(jsonl_content)
        jsonl_file = Path(f.name)
    
    try:
        # Test reading
        with JSONLReader(jsonl_file) as reader:
            rows = list(reader)
            assert len(rows) == 3
            assert rows[0] == {"name": "Alice", "age": 25, "city": "New York"}
            assert rows[1] == {"name": "Bob", "age": 30, "city": "San Francisco"}
            assert rows[2] == {"name": "Charlie", "age": 35, "city": "Chicago"}
    finally:
        jsonl_file.unlink()


def test_text_reader():
    """Test text file reading."""
    # Create temporary text file
    text_content = """line 1
line 2
line 3"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        text_file = Path(f.name)
    
    try:
        # Test reading
        with TextReader(text_file) as reader:
            rows = list(reader)
            assert len(rows) == 3
            assert rows[0] == "line 1"
            assert rows[1] == "line 2"
            assert rows[2] == "line 3"
    finally:
        text_file.unlink()


def test_parse_file_csv():
    """Test parse_file function with CSV."""
    csv_content = """name,age
Alice,25
Bob,30"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file = Path(f.name)
    
    try:
        with parse_file(csv_file) as reader:
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == {"name": "Alice", "age": "25"}
        assert rows[1] == {"name": "Bob", "age": "30"}
    finally:
        csv_file.unlink()


def test_write_file_csv():
    """Test write_file function with CSV."""
    data = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
    ]
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        output_file = Path(f.name)
    
    try:
        write_file(output_file, data)
        
        # Read back and verify
        with parse_file(output_file) as reader:
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == {"name": "Alice", "age": "25"}
        assert rows[1] == {"name": "Bob", "age": "30"}
    finally:
        output_file.unlink()


def test_detect_csv_delimiter():
    """Test CSV delimiter detection."""
    # Create temp files with different delimiters
    csv_comma = "a,b,c\n1,2,3"
    csv_tab = "a\tb\tc\n1\t2\t3"
    csv_semicolon = "a;b;c\n1;2;3"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_comma)
        comma_file = Path(f.name)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as f:
        f.write(csv_tab)
        tab_file = Path(f.name)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_semicolon)
        semicolon_file = Path(f.name)
    
    try:
        assert detect_csv_delimiter(comma_file) == ","
        assert detect_csv_delimiter(tab_file) == "\t"
        assert detect_csv_delimiter(semicolon_file) == ";"
    finally:
        comma_file.unlink()
        tab_file.unlink()
        semicolon_file.unlink()
