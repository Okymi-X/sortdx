"""
sortdx - Universal sorting tool and library

A powerful Python library and CLI tool for sorting any kind of data:
- In-memory data structures (lists, dicts)
- Files (CSV, JSONL, TXT, compressed)
- Large datasets using external sorting algorithms

Example usage:
    >>> import sortdx
    >>> data = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
    >>> sorted_data = sortdx.sort_iter(data, keys=[sortdx.key("age", "num")])
    >>> list(sorted_data)
    [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
"""

from .core import key, sort_file, sort_iter
from .utils import SortKey, SortStats

__version__ = "0.1.0"
__author__ = "sortdx contributors"
__email__ = "dev@sortdx.io"

__all__ = [
    "key",
    "sort_file",
    "sort_iter",
    "SortKey",
    "SortStats",
]
