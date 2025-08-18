# sortx

[![Build Status](https://github.com/Okymi-X/sortx/workflows/CI/badge.svg)](https://github.com/Okymi-X/sortx/actions)
[![PyPI version](https://badge.fury.io/py/sortx.svg)](https://badge.fury.io/py/sortx)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**sortx** is a universal sorting tool and library for Python that can sort anything: arrays, lists, dictionaries, CSV/TSV files, JSONL, plain text, and even massive datasets (multi-GB) using external sorting algorithms.

## Features

🚀 **Universal Sorting**: Sort any data format (CSV, JSONL, TXT, compressed files)  
📊 **Multi-key Sorting**: Sort by multiple columns with different data types  
⚡ **External Sorting**: Handle massive files that don't fit in memory  
🌍 **Locale-aware**: Support for international text sorting  
🔧 **Smart Detection**: Automatically detect file formats and separators  
📦 **Easy Installation**: `pip install sortx`  
🛠️ **CLI + Library**: Use as command-line tool or Python library  

## Installation

```bash
pip install sortx
```

## Quick Start

### Command Line Interface

```bash
# Sort CSV by price (numeric), then name (string with French locale)
sortx data.csv -o sorted.csv -k price:num -k name:str:locale=fr

# Sort large JSONL file by timestamp with memory limit
sortx logs.jsonl.gz -o sorted.jsonl.gz -k timestamp:date --memory-limit=512M

# Natural sort of text file (file2 comes before file10)
sortx filenames.txt -o sorted.txt --natural

# Sort with uniqueness constraint
sortx users.jsonl -o unique_users.jsonl -k created_at:date --unique=id
```

### Python API

```python
import sortx

# Sort in-memory data
data = [
    {"name": "Zoé", "price": "9.8"},
    {"name": "André", "price": "10.0"}
]

sorted_data = sortx.sort_iter(
    data,
    keys=[
        sortx.key("price", "num"),
        sortx.key("name", "str", locale="fr")
    ]
)

# Sort file to file
sortx.sort_file(
    "input.jsonl",
    "output.jsonl", 
    keys=[sortx.key("created_at", "date", desc=True)],
    unique="id"
)
```

## Data Types

sortx supports multiple data types for sorting keys:

- **`num`**: Numeric sorting (integers, floats)
- **`str`**: String sorting with locale support
- **`date`**: Date/time sorting (ISO 8601, common formats)
- **`nat`**: Natural sorting ("file2" < "file10")

## File Formats

- **CSV/TSV**: Automatic delimiter detection
- **JSONL**: One JSON object per line
- **TXT**: Plain text, line-by-line sorting
- **Compressed**: `.gz` and `.zst` support
- **Large files**: External sorting for files that don't fit in memory

## Command Line Options

```bash
sortx [INPUT] [OPTIONS]

Options:
  -o, --output FILE          Output file path
  -k, --key KEY_SPEC         Sort key (format: column:type[:options])
  --reverse                  Sort in descending order
  --stable / --unstable      Stable sorting (default: stable)
  --unique COLUMN            Keep only unique values for specified column
  --locale LOCALE           Locale for string sorting (e.g., fr_FR.UTF-8)
  --memory-limit SIZE       Memory limit for external sorting (e.g., 512M, 2G)
  --stats                   Show sorting statistics
  --natural                 Use natural sorting for all string columns
  --help                    Show help message
```

### Key Specification Format

Sort keys use the format: `column:type[:option=value]`

Examples:
- `price:num` - Sort by price as number
- `name:str:locale=fr` - Sort by name with French locale
- `date:date:desc=true` - Sort by date in descending order
- `filename:nat` - Natural sort by filename

## Examples

### CSV Sorting

```bash
# Sort sales data by region, then by revenue (descending)
sortx sales.csv -o sorted_sales.csv \
  -k region:str \
  -k revenue:num:desc=true
```

Input (`sales.csv`):
```csv
region,product,revenue
North,Widget A,1000
South,Widget B,1500
North,Widget C,800
South,Widget A,1200
```

Output:
```csv
region,product,revenue
North,Widget A,1000
North,Widget C,800
South,Widget B,1500
South,Widget A,1200
```

### JSONL Sorting

```bash
# Sort user logs by timestamp
sortx user_logs.jsonl -o sorted_logs.jsonl -k timestamp:date
```

Input (`user_logs.jsonl`):
```json
{"user_id": 123, "action": "login", "timestamp": "2025-01-15T10:30:00Z"}
{"user_id": 456, "action": "logout", "timestamp": "2025-01-15T09:15:00Z"}
{"user_id": 123, "action": "view_page", "timestamp": "2025-01-15T10:35:00Z"}
```

### Large File Processing

```bash
# Sort 10GB log file with 1GB memory limit
sortx huge_logs.jsonl.gz -o sorted_huge.jsonl.gz \
  -k timestamp:date \
  --memory-limit=1G \
  --stats
```

## Performance

sortx is designed for performance:

- **Streaming**: Processes files line-by-line to minimize memory usage
- **External Sorting**: Handles files larger than available RAM
- **Optimized Parsing**: Fast CSV/JSON parsing with minimal overhead
- **Parallel Processing**: Multi-threaded sorting for large datasets

## Development

### Setup Development Environment

```bash
git clone https://github.com/Okymi-X/sortx.git
cd sortx
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black sortx tests
isort sortx tests
flake8 sortx tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Rust core implementation for better performance
- [ ] Additional file formats (Parquet, Avro)
- [ ] Distributed sorting across multiple machines
- [ ] GUI interface
- [ ] More compression formats (bz2, xz, lz4)

## Acknowledgments

- Inspired by GNU sort and other Unix sorting utilities
- Built with Python's robust ecosystem for data processing
