"""
Test file parsing functionality.
"""

import json
import tempfile
from pathlib import Path

import pytest
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
    
    # Compressed files
    assert detect_format("data.csv.gz") == "csv"
    assert detect_format("data.jsonl.gz") == "jsonl"
    assert detect_format("data.txt.zst") == "txt"


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


def test_detect_csv_delimiter():
    """Test CSV delimiter detection."""
    # Comma-separated
    csv_content = "name,age,city\nAlice,25,New York"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file = Path(f.name)
    
    try:
        delimiter = detect_csv_delimiter(csv_file)
        assert delimiter == ","
    finally:
        csv_file.unlink()
    
    # Semicolon-separated
    csv_content = "name;age;city\nAlice;25;New York"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file = Path(f.name)
    
    try:
        delimiter = detect_csv_delimiter(csv_file)
        assert delimiter == ";"
    finally:
        csv_file.unlink()


def test_jsonl_reader():
    """Test JSONL file reading."""
    # Create temporary JSONL file
    jsonl_content = '''{"name": "Alice", "age": 25}
{"name": "Bob", "age": 30}
{"name": "Charlie", "age": 35}'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write(jsonl_content)
        jsonl_file = Path(f.name)
    
    try:
        # Test reading
        with JSONLReader(jsonl_file) as reader:
            rows = list(reader)
        
        assert len(rows) == 3
        assert rows[0] == {"name": "Alice", "age": 25}
        assert rows[1] == {"name": "Bob", "age": 30}
        assert rows[2] == {"name": "Charlie", "age": 35}
        
    finally:
        jsonl_file.unlink()


def test_text_reader():
    """Test plain text file reading."""
    # Create temporary text file
    text_content = """line1
line2
line3
line4"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(text_content)
        text_file = Path(f.name)
    
    try:
        # Test reading
        with TextReader(text_file) as reader:
            lines = list(reader)
        
        assert len(lines) == 4
        assert lines == ["line1", "line2", "line3", "line4"]
        
    finally:
        text_file.unlink()


def test_parse_file():
    """Test the parse_file context manager."""
    # CSV file
    csv_content = "name,age\nAlice,25\nBob,30"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file = Path(f.name)
    
    try:
        with parse_file(csv_file) as reader:
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
    finally:
        csv_file.unlink()
    
    # JSONL file
    jsonl_content = '{"name": "Alice"}\n{"name": "Bob"}'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write(jsonl_content)
        jsonl_file = Path(f.name)
    
    try:
        with parse_file(jsonl_file) as reader:
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
    finally:
        jsonl_file.unlink()


def test_write_file_jsonl():
    """Test writing JSONL files."""
    data = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
    ]
    
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        output_file = Path(f.name)
    
    try:
        write_file(output_file, data, "jsonl")
        
        # Read back and verify
        with parse_file(output_file) as reader:
            result = list(reader)
        
        assert len(result) == 2
        assert result[0] == {"name": "Alice", "age": 25}
        assert result[1] == {"name": "Bob", "age": 30}
        
    finally:
        output_file.unlink()


def test_write_file_csv():
    """Test writing CSV files."""
    data = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
    ]
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        output_file = Path(f.name)
    
    try:
        write_file(output_file, data, "csv")
        
        # Read back and verify
        with parse_file(output_file) as reader:
            result = list(reader)
        
        assert len(result) == 2
        assert result[0]["name"] == "Alice"
        assert result[1]["name"] == "Bob"
        
    finally:
        output_file.unlink()


def test_write_file_txt():
    """Test writing text files."""
    data = ["line1", "line2", "line3"]
    
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        output_file = Path(f.name)
    
    try:
        write_file(output_file, data, "txt")
        
        # Read back and verify
        with parse_file(output_file) as reader:
            result = list(reader)
        
        assert len(result) == 3
        assert result == ["line1", "line2", "line3"]
        
    finally:
        output_file.unlink()
