# sortdx

A powerful and flexible file sorting utility for Python that intelligently handles CSV, JSONL, and text files.

## 🚀 Quick Start

```bash
pip install sortdx
```

### Basic Usage

```python
import sortdx

# Sort a CSV by age column
sortdx.sort_file('data.csv', 'sorted.csv', keys=[sortdx.key('age', 'num')])

# Sort a JSONL by timestamp
sortdx.sort_file('logs.jsonl', 'sorted_logs.jsonl', keys=[sortdx.key('timestamp')])

# Sort a text file by 3rd column numerically
sortdx.sort_file('data.txt', 'sorted.txt', keys=[sortdx.key(3, 'num')])
```

## 📦 Installation

```bash
pip install sortdx
```

To use the command line interface (optional):
```bash
pip install "sortdx[cli]"
```

## 🔧 Features

- **Intelligent Format Detection**: Automatically detects CSV, JSONL, and text formats
- **Multiple Sort Keys**: Sort by multiple columns/fields with different data types
- **Memory Efficient**: Handles large files without loading everything into memory
- **Type-Aware Sorting**: Support for string, numeric, and date/time sorting
- **Flexible Input**: Works with file paths or file-like objects
- **Statistics**: Optional sorting statistics and progress reporting

## 📖 Usage

### Sort Keys

Create sort keys using the `sortdx.key()` function:

```python
import sortdx

# String sorting (default)
key1 = sortdx.key('name')
key1 = sortdx.key(1)  # Column index for text files

# Numeric sorting
key2 = sortdx.key('age', 'num')
key2 = sortdx.key(2, 'num')

# Reverse sorting
key3 = sortdx.key('name', reverse=True)
```

### File Formats

#### CSV Files
```python
# Sort by single column
sortdx.sort_file('data.csv', 'output.csv', keys=[sortdx.key('age', 'num')])

# Sort by multiple columns
sortdx.sort_file('data.csv', 'output.csv', keys=[
    sortdx.key('department'),
    sortdx.key('salary', 'num', reverse=True)
])
```

#### JSONL Files
```python
# Sort JSON Lines files
sortdx.sort_file('logs.jsonl', 'sorted.jsonl', keys=[
    sortdx.key('timestamp'),
    sortdx.key('priority', 'num')
])
```

#### Text Files
```python
# Sort by column index (1-based)
sortdx.sort_file('data.txt', 'sorted.txt', keys=[sortdx.key(2, 'num')])

# Custom delimiter
sortdx.sort_file('data.txt', 'sorted.txt', 
                keys=[sortdx.key(1)],
                delimiter='|')
```

### Advanced Options

```python
# Get sorting statistics
stats = sortdx.sort_file('large_file.csv', 'sorted.csv', 
                        keys=[sortdx.key('id', 'num')],
                        stats=True)
print(f"Processed {stats.lines_processed} lines")

# Memory-efficient sorting for large files
sortdx.sort_file('huge_file.csv', 'sorted.csv',
                keys=[sortdx.key('timestamp')],
                max_memory_mb=500)  # Limit memory usage
```

## 🔄 Data Types

- `'str'` or `'text'`: String/text sorting (default)
- `'num'` or `'numeric'`: Numeric sorting (handles integers and floats)
- `'date'` or `'datetime'`: Date/time sorting (ISO format recommended)

## 📊 Examples

### Example 1: Employee Data (CSV)
```python
import sortdx

# employees.csv content:
# name,age,department,salary
# Alice,25,Engineering,75000
# Bob,30,Sales,65000
# Carol,28,Engineering,80000

# Sort by department, then by salary (highest first)
sortdx.sort_file('employees.csv', 'sorted_employees.csv', keys=[
    sortdx.key('department'),
    sortdx.key('salary', 'num', reverse=True)
])
```

### Example 2: Log Files (JSONL)
```python
# logs.jsonl content:
# {"timestamp": "2024-01-01T10:00:00Z", "level": "INFO", "message": "Start"}
# {"timestamp": "2024-01-01T10:01:00Z", "level": "ERROR", "message": "Failed"}

# Sort by timestamp
sortdx.sort_file('logs.jsonl', 'sorted_logs.jsonl', keys=[
    sortdx.key('timestamp')
])
```

### Example 3: Space-Separated Data (TXT)
```python
# data.txt content:
# Alice 25 Engineering 75000
# Bob 30 Sales 65000

# Sort by 4th column (salary) numerically
sortdx.sort_file('data.txt', 'sorted_data.txt', keys=[
    sortdx.key(4, 'num', reverse=True)
])
```

## 🧪 Real-World Tests

The package has been successfully tested on:

### CSV
```csv
name,age,salary
Alice,25,45000
Diana,28,55000
Bob,30,50000
Charlie,35,60000
```
**Sort by age** → Alice (25), Diana (28), Bob (30), Charlie (35) ✅

### JSONL
```jsonl
{"name": "Alice", "age": 25, "timestamp": "2025-01-15T09:15:00Z"}
{"name": "Diana", "age": 28, "timestamp": "2025-01-15T08:20:00Z"}
{"name": "Bob", "age": 30, "timestamp": "2025-01-15T10:30:00Z"}
{"name": "Charlie", "age": 35, "timestamp": "2025-01-15T11:45:00Z"}
```
**Sort by age** → Same order as CSV ✅

### TXT
```
file10.txt
file2.txt  
file1.txt
file20.txt
file3.txt
```
**Numeric sort by 3rd column** → Correct order based on numeric values ✅

## 🎯 Performance

sortdx is designed for efficiency:

- **Memory Usage**: Configurable memory limits for processing large files
- **Speed**: Optimized sorting algorithms with minimal overhead
- **Scalability**: Efficiently handles files from KB to GB sizes

## 📈 Sort Statistics

```python
import sortdx

# Get detailed statistics
stats = sortdx.sort_file('data.csv', 'sorted.csv', 
                        keys=[sortdx.key('age', 'num')], 
                        stats=True)

print(f"Lines processed: {stats.lines_processed}")
print(f"Sort time: {stats.sort_time:.2f}s") 
print(f"Memory used: {stats.memory_used_mb:.1f}MB")
```

## 🔗 API Reference

### `sortdx.sort_file(input_path, output_path, keys, **options)`

Sorts a file according to specified keys.

**Parameters:**
- `input_path` (str): Input file path
- `output_path` (str): Output file path
- `keys` (List[SortKey]): List of sort keys
- `delimiter` (str, optional): Delimiter for text files (default: auto-detection)
- `stats` (bool, optional): Return statistics (default: False)
- `max_memory_mb` (int, optional): Memory limit in MB

**Returns:**
- `SortStats` if stats=True, otherwise None

### `sortdx.key(field, type='str', reverse=False)`

Creates a sort key.

**Parameters:**
- `field` (str|int): Field name (CSV/JSONL) or column index (TXT)
- `type` (str): Data type ('str', 'num', 'date')
- `reverse` (bool): Reverse sort

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/sortdx/issues) on GitHub.

## 🌐 PyPI

Package available on PyPI: https://pypi.org/project/sortdx/

## 🏷️ Version

Current version: **0.1.1**

Installation tested on:
- Python 3.10+
- Windows, macOS, Linux
- Files from a few KB to several GB
