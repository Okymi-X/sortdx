# sortx

[![Build Status](https://github.com/Okymi-X/sortx/workflows/CI/badge.svg)](https://github.com/Okymi-X/sortx/actions)
[![PyPI version](https://badge.fury.io/py/sortx.svg)](https://badge.fury.io/py/sortx)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**sortx** is a powerful, universal sorting tool and Python library designed to sort any kind of data: in-memory data structures, CSV/JSONL files, plain text, and even massive datasets using efficient external sorting algorithms.

## ✨ Features

🚀 **Universal Sorting**: Sort any data format (CSV, JSONL, TXT, compressed files)  
📊 **Multi-key Sorting**: Sort by multiple columns with different data types and directions  
⚡ **External Sorting**: Handle massive files that don't fit in memory using external merge sort  
🌍 **Locale-aware**: International text sorting with locale support  
🔧 **Smart Detection**: Automatically detect file formats and separators  
📦 **Easy Installation**: Simple `pip install sortx`  
🛠️ **CLI + Library**: Use as command-line tool or import as Python library  
🎯 **Type Support**: Numbers, strings, dates, natural sorting  
🔄 **Stable Sorting**: Preserves original order for equal elements  
🎛️ **Flexible Options**: Reverse, unique constraints, memory limits  

## 📦 Installation

### Basic Installation
```bash
pip install sortx
```

### Full Installation (with CLI and enhanced features)
```bash
pip install sortx[full]
```

The full installation includes:
- `typer` and `rich` for beautiful CLI experience
- `python-dateutil` for advanced date parsing
- `natsort` for natural sorting
- `chardet` for encoding detection

## 🚀 Quick Start

### Command Line Interface

```bash
# Sort CSV by price (numeric), then name (alphabetic)
sortx data.csv -o sorted.csv -k price:num -k name:str

# Sort large JSONL file by timestamp with memory limit
sortx logs.jsonl.gz -o sorted.jsonl.gz -k timestamp:date --memory-limit=512M

# Natural sort of text file (file2 comes before file10)
sortx filenames.txt -o sorted.txt -k 0:nat

# Sort with uniqueness constraint
sortx users.jsonl -o unique_users.jsonl -k created_at:date --unique=id

# Show sorting statistics
sortx large_data.csv -o sorted_data.csv -k score:num:desc=true --stats
```

### Python Library

```python
import sortx

# Sort in-memory data
data = [
    {"name": "Alice", "age": 30, "salary": 50000},
    {"name": "Bob", "age": 25, "salary": 45000},
    {"name": "Charlie", "age": 35, "salary": 60000}
]

# Single key sorting
sorted_by_age = list(sortx.sort_iter(
    data, 
    keys=[sortx.key("age", "num")]
))

# Multi-key sorting
sorted_multi = list(sortx.sort_iter(
    data,
    keys=[
        sortx.key("salary", "num", desc=True),  # Salary descending
        sortx.key("name", "str")                # Then name ascending
    ]
))

# Sort file to file
stats = sortx.sort_file(
    input_path="input.csv",
    output_path="output.csv", 
    keys=[sortx.key("created_at", "date", desc=True)],
    stats=True
)
print(f"Processed {stats.lines_processed} lines in {stats.processing_time:.2f}s")
```

## 📊 Data Types

sortx supports multiple data types for sorting keys:

| Type | Description | Example |
|------|-------------|---------|
| **`num`** | Numeric sorting (integers, floats) | `42`, `3.14`, `-10` |
| **`str`** | String sorting with locale support | `"Alice"`, `"café"` |
| **`date`** | Date/time sorting (ISO 8601 + common formats) | `"2025-01-15"`, `"2025-01-15T10:30:00Z"` |
| **`nat`** | Natural sorting ("file2" < "file10") | `"file1.txt"`, `"file10.txt"` |

### Date Format Support
- ISO 8601: `2025-01-15T10:30:00Z`
- Common formats: `2025-01-15`, `01/15/2025`, `Jan 15, 2025`
- Automatic parsing with `python-dateutil` (when installed)

## 📁 File Format Support

| Format | Extensions | Compression | Description |
|--------|------------|-------------|-------------|
| **CSV/TSV** | `.csv`, `.tsv` | ✅ | Automatic delimiter detection |
| **JSONL** | `.jsonl`, `.ndjson` | ✅ | One JSON object per line |
| **Plain Text** | `.txt`, any | ✅ | Line-by-line sorting |
| **Compressed** | `.gz`, `.zst` | - | Transparent compression support |

### Large File Handling
- **External Sorting**: Automatically handles files larger than available RAM
- **Memory Limits**: Configurable memory usage (`--memory-limit=512M`)
- **Streaming**: Processes files line-by-line to minimize memory footprint

## 🔧 Command Line Reference

```bash
sortx [INPUT] [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output FILE` | `-o` | Output file path |
| `--key KEY_SPEC` | `-k` | Sort key specification (can be used multiple times) |
| `--reverse` | | Reverse the entire sort order |
| `--stable` | | Use stable sorting (default) |
| `--unique COLUMN` | | Keep only unique values for specified column |
| `--memory-limit SIZE` | | Memory limit for external sorting (e.g., 512M, 2G) |
| `--stats` | | Show detailed sorting statistics |
| `--help` | `-h` | Show help message |

### Key Specification Format

Sort keys use the format: `column:type[:desc=true][:locale=name]`

**Examples:**
- `price:num` - Sort by price as number (ascending)
- `price:num:desc=true` - Sort by price as number (descending)
- `name:str:locale=fr_FR` - Sort by name with French locale
- `timestamp:date` - Sort by timestamp as date
- `0:nat` - Natural sort by first column (for text files)

## 💡 Examples

### Example 1: Sales Data Analysis

**Input (`sales.csv`):**
```csv
region,product,revenue,date
North,Widget A,1000,2025-01-15
South,Widget B,1500,2025-01-14
North,Widget C,800,2025-01-16
South,Widget A,1200,2025-01-13
```

**Command:**
```bash
sortx sales.csv -o sorted_sales.csv -k region:str -k revenue:num:desc=true
```

**Output:**
```csv
region,product,revenue,date
North,Widget A,1000,2025-01-15
North,Widget C,800,2025-01-16
South,Widget B,1500,2025-01-14
South,Widget A,1200,2025-01-13
```

### Example 2: Log File Processing

**Input (`server.jsonl`):**
```json
{"timestamp": "2025-01-15T10:30:00Z", "level": "ERROR", "message": "Connection failed"}
{"timestamp": "2025-01-15T10:25:00Z", "level": "INFO", "message": "Server started"}
{"timestamp": "2025-01-15T10:35:00Z", "level": "WARN", "message": "High memory usage"}
```

**Command:**
```bash
sortx server.jsonl -o sorted_logs.jsonl -k timestamp:date --stats
```

**Output includes statistics:**
```
Sorting Statistics:
  Input file: server.jsonl
  Output file: sorted_logs.jsonl
  Lines processed: 3
  Processing time: 0.01s
  Input size: 312B
  Output size: 312B
  External sort: No
  Throughput: 300 lines/sec
```

### Example 3: Large Dataset Processing

**Processing a 5GB file:**
```bash
sortx huge_dataset.csv.gz -o sorted_huge.csv.gz \
  -k timestamp:date \
  -k user_id:num \
  --memory-limit=1G \
  --unique=transaction_id \
  --stats
```

This command:
- Sorts by timestamp, then user_id
- Uses maximum 1GB of RAM (external sort for larger files)
- Removes duplicate transactions
- Shows detailed performance statistics

## 🐍 Python API Reference

### Core Functions

#### `sortx.key(column, data_type, desc=False, locale_name=None, **options)`
Create a sort key specification.

**Parameters:**
- `column`: Column name (dict) or index (list/tuple)
- `data_type`: Data type (`'str'`, `'num'`, `'date'`, `'nat'`)
- `desc`: Sort in descending order if True
- `locale_name`: Locale for string sorting (e.g., `'fr_FR.UTF-8'`)

#### `sortx.sort_iter(data, keys, stable=True, reverse=False, unique=None)`
Sort an iterator of data in memory.

**Parameters:**
- `data`: Iterator of items to sort
- `keys`: List of SortKey specifications
- `stable`: Use stable sorting algorithm
- `reverse`: Reverse the entire sort order
- `unique`: Column name for uniqueness constraint

#### `sortx.sort_file(input_path, output_path, keys, memory_limit=None, stats=False, **options)`
Sort a file and write results to another file.

**Parameters:**
- `input_path`: Path to input file
- `output_path`: Path to output file
- `keys`: List of SortKey specifications
- `memory_limit`: Memory limit string (e.g., `'512M'`, `'2G'`)
- `stats`: Return sorting statistics

### Advanced Usage

```python
import sortx

# Complex multi-key sorting with different options per key
keys = [
    sortx.key("department", "str"),                    # Primary: department
    sortx.key("salary", "num", desc=True),            # Secondary: salary (desc)
    sortx.key("hire_date", "date"),                   # Tertiary: hire date
    sortx.key("name", "str", locale_name="en_US")     # Quaternary: name
]

result = list(sortx.sort_iter(employee_data, keys=keys))

# File sorting with memory management and statistics
stats = sortx.sort_file(
    input_path="employees.csv",
    output_path="sorted_employees.csv",
    keys=keys,
    memory_limit="256M",  # Use max 256MB RAM
    unique="employee_id", # Remove duplicates by employee ID
    stats=True           # Return detailed statistics
)

print(f"Sorted {stats.lines_processed} employees")
print(f"Processing time: {stats.processing_time:.2f} seconds")
print(f"Throughput: {stats.throughput:.0f} lines/second")
```

## ⚡ Performance

sortx is optimized for performance across different scenarios:

### In-Memory Sorting
- **Fast**: Optimized Python sorting with custom key functions
- **Memory Efficient**: Streaming processing where possible
- **Stable**: Maintains relative order of equal elements

### External Sorting (Large Files)
- **Scalable**: Handles files larger than available RAM
- **Configurable**: Memory usage limits prevent system overload
- **Efficient**: Multi-way merge sort with optimized I/O

### Benchmarks (Approximate)

| File Size | Records | Memory Limit | Processing Time | Throughput |
|-----------|---------|-------------|----------------|------------|
| 100MB | 1M | 512MB | 5s | 200K lines/sec |
| 1GB | 10M | 512MB | 60s | 167K lines/sec |
| 10GB | 100M | 1GB | 15min | 111K lines/sec |

*Benchmarks run on modern hardware (SSD, 16GB RAM). Performance varies based on data complexity and system specifications.*

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Okymi-X/sortx.git
cd sortx

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[full,dev]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=sortx --cov-report=html

# Run specific test file
pytest tests/test_core.py
```

### Code Quality

```bash
# Format code
black sortx tests

# Sort imports
isort sortx tests

# Lint code
flake8 sortx tests

# Type checking
mypy sortx
```

### Running Demo

```bash
# Quick demo
python demo.py

# Comprehensive tests
python main.py
```

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes and add tests
4. **Ensure** code quality (`black`, `isort`, `flake8`, `pytest`)
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Areas for Contribution
- 🚀 Performance optimizations
- 📊 Additional file format support
- 🌍 Locale and internationalization improvements
- 📚 Documentation and examples
- 🧪 Test coverage expansion
- 🔧 CLI enhancements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🗺️ Roadmap

### Version 0.2.0
- [ ] Rust core implementation for 10x performance boost
- [ ] Additional compression formats (bz2, xz, lz4)
- [ ] Memory-mapped file support for better performance
- [ ] Progress bars for long-running operations

### Version 0.3.0
- [ ] Additional file formats (Parquet, Avro, Excel)
- [ ] Database integration (PostgreSQL, SQLite)
- [ ] Parallel sorting with multiple CPU cores
- [ ] Advanced statistics and profiling

### Version 1.0.0
- [ ] Distributed sorting across multiple machines
- [ ] Web-based GUI interface
- [ ] Plugin system for custom data types
- [ ] Real-time streaming sort capabilities

## 🙏 Acknowledgments

- Inspired by **GNU sort** and other Unix sorting utilities
- Built with Python's robust ecosystem for data processing
- Uses **external sorting algorithms** from computer science literature
- Thanks to the open source community for excellent libraries:
  - `typer` and `rich` for beautiful CLI
  - `python-dateutil` for date parsing
  - `natsort` for natural sorting

## 📞 Support

- 📖 **Documentation**: [GitHub README](https://github.com/Okymi-X/sortx#readme)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Okymi-X/sortx/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Okymi-X/sortx/discussions)
- 📧 **Email**: dev@sortx.io

---
