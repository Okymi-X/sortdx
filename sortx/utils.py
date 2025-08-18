"""
Utility classes and functions for sortx.

This module contains helper classes like SortKey and SortStats,
as well as utility functions for memory parsing and formatting.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union


@dataclass
class SortKey:
    """
    Specification for a sort key.
    
    Attributes:
        column: Column name (for dicts) or index (for lists/tuples)
        data_type: Type of data ('str', 'num', 'date', 'nat')
        desc: Sort in descending order if True
        locale_name: Locale for string sorting
        options: Additional type-specific options
    """
    column: Union[str, int]
    data_type: str = "str"
    desc: bool = False
    locale_name: Optional[str] = None
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}
        
        # Handle desc option from options dict
        if "desc" in self.options:
            self.desc = bool(self.options["desc"])
        
        # Handle locale option from options dict
        if "locale" in self.options:
            self.locale_name = self.options["locale"]


@dataclass
class SortStats:
    """
    Statistics about a sorting operation.
    
    Attributes:
        input_file: Path to input file
        output_file: Path to output file
        lines_processed: Number of lines processed
        processing_time: Time taken in seconds
        input_size: Input file size in bytes
        output_size: Output file size in bytes
        external_sort_used: Whether external sorting was used
    """
    input_file: str
    output_file: str
    lines_processed: int
    processing_time: float
    input_size: int
    output_size: int
    external_sort_used: bool
    
    def __str__(self) -> str:
        """Format statistics for display."""
        return (
            f"Sorting Statistics:\n"
            f"  Input file: {self.input_file}\n"
            f"  Output file: {self.output_file}\n"
            f"  Lines processed: {self.lines_processed:,}\n"
            f"  Processing time: {self.processing_time:.2f}s\n"
            f"  Input size: {format_size(self.input_size)}\n"
            f"  Output size: {format_size(self.output_size)}\n"
            f"  External sort: {'Yes' if self.external_sort_used else 'No'}\n"
            f"  Throughput: {self.lines_processed / self.processing_time:.0f} lines/sec"
        )


def parse_memory_size(size_str: str) -> int:
    """
    Parse memory size string into bytes.
    
    Args:
        size_str: Memory size (e.g., '512M', '2G', '1024K')
        
    Returns:
        Size in bytes
        
    Example:
        >>> parse_memory_size('512M')
        536870912
        >>> parse_memory_size('2G')
        2147483648
    """
    size_str = size_str.strip().upper()
    
    # Extract number and unit
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?)B?$', size_str)
    if not match:
        raise ValueError(f"Invalid memory size format: {size_str}")
    
    number = float(match.group(1))
    unit = match.group(2) or ''
    
    multipliers = {
        '': 1,
        'K': 1024,
        'M': 1024 ** 2,
        'G': 1024 ** 3,
        'T': 1024 ** 4,
    }
    
    if unit not in multipliers:
        raise ValueError(f"Invalid memory unit: {unit}")
    
    return int(number * multipliers[unit])


def format_size(bytes_size: int) -> str:
    """
    Format byte size into human-readable string.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted size string
        
    Example:
        >>> format_size(1024)
        '1.0K'
        >>> format_size(1536)
        '1.5K'
    """
    if bytes_size == 0:
        return "0B"
    
    units = ['B', 'K', 'M', 'G', 'T']
    unit_index = 0
    size = float(bytes_size)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)}B"
    else:
        return f"{size:.1f}{units[unit_index]}"


def parse_key_spec(key_spec: str) -> SortKey:
    """
    Parse a key specification string into a SortKey object.
    
    Args:
        key_spec: Key specification (e.g., 'price:num', 'name:str:locale=fr')
        
    Returns:
        SortKey object
        
    Example:
        >>> key = parse_key_spec('price:num:desc=true')
        >>> key.column
        'price'
        >>> key.data_type
        'num'
        >>> key.desc
        True
    """
    if not key_spec.strip():
        raise ValueError(f"Invalid key specification: {key_spec}")
    
    parts = key_spec.split(':')
    
    if len(parts) < 1:
        raise ValueError(f"Invalid key specification: {key_spec}")
    
    column = parts[0]
    if not column.strip():
        raise ValueError(f"Invalid key specification: {key_spec}")
    
    data_type = parts[1] if len(parts) > 1 else "str"
    
    # Parse options
    options = {}
    for part in parts[2:]:
        if '=' in part:
            key, value = part.split('=', 1)
            # Convert common values
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            options[key] = value
        else:
            # Treat as boolean flag
            options[part] = True
    
    # Try to convert column to int if it looks like an index
    try:
        column = int(column)
    except ValueError:
        pass  # Keep as string
    
    return SortKey(
        column=column,
        data_type=data_type,
        options=options
    )


def validate_sort_keys(keys: list) -> None:
    """
    Validate a list of sort keys.
    
    Args:
        keys: List of SortKey objects
        
    Raises:
        ValueError: If any key is invalid
    """
    valid_types = {'str', 'num', 'date', 'nat'}
    
    for i, key in enumerate(keys):
        if not isinstance(key, SortKey):
            raise ValueError(f"Key {i} is not a SortKey object")
        
        if key.data_type not in valid_types:
            raise ValueError(
                f"Key {i} has invalid data type '{key.data_type}'. "
                f"Valid types: {', '.join(valid_types)}"
            )
        
        if key.column is None or key.column == "":
            raise ValueError(f"Key {i} has empty column specification")


class ProgressTracker:
    """Simple progress tracker for file operations."""
    
    def __init__(self, total: int = 0, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self._last_percent = -1
    
    def update(self, increment: int = 1) -> None:
        """Update progress by increment."""
        self.current += increment
        self._maybe_print_progress()
    
    def set_current(self, current: int) -> None:
        """Set current progress value."""
        self.current = current
        self._maybe_print_progress()
    
    def _maybe_print_progress(self) -> None:
        """Print progress if percentage changed significantly."""
        if self.total <= 0:
            return
        
        percent = int((self.current / self.total) * 100)
        if percent != self._last_percent and percent % 10 == 0:
            print(f"{self.description}: {percent}% ({self.current:,}/{self.total:,})")
            self._last_percent = percent
    
    def finish(self) -> None:
        """Mark progress as complete."""
        if self.total > 0:
            print(f"{self.description}: 100% ({self.total:,}/{self.total:,})")


def get_file_line_count(file_path: str) -> int:
    """
    Get approximate line count of a file efficiently.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Estimated number of lines
    """
    try:
        with open(file_path, 'rb') as f:
            # Count newlines in chunks
            chunk_size = 8192
            line_count = 0
            
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                line_count += chunk.count(b'\n')
            
            return line_count
    except Exception:
        return 0


def ensure_output_dir(file_path: str) -> None:
    """
    Ensure the output directory exists.
    
    Args:
        file_path: Path to output file
    """
    from pathlib import Path
    
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
