"""
Core sorting functionality for sortdx.

This module provides the main sorting algorithms and key creation functions
for in-memory and file-based sorting operations.
"""

import heapq
import locale
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterator, List, Optional, Union

try:
    from dateutil import parser as date_parser
except ImportError:
    # Fallback for missing dateutil
    import datetime

    class DateParser:
        @staticmethod
        def parse(date_string):
            # Simple ISO format fallback
            try:
                return datetime.datetime.fromisoformat(
                    date_string.replace("Z", "+00:00")
                )
            except:
                return datetime.datetime(1900, 1, 1)

    date_parser = DateParser()

try:
    from natsort import natsorted, ns
except ImportError:
    # Fallback for missing natsort
    def natsorted(items, alg=None):
        return sorted(items)

    class NS:
        IGNORECASE = 0

    ns = NS()

from .parsers import detect_format, parse_file, write_file
from .utils import SortKey, SortStats, parse_memory_size


def key(
    column: Union[str, int],
    data_type: str = "str",
    desc: bool = False,
    locale_name: Optional[str] = None,
    **options: Any,
) -> SortKey:
    """
    Create a sort key specification.

    Args:
        column: Column name (for dicts) or index (for lists/tuples)
        data_type: Type of data ('str', 'num', 'date', 'nat')
        desc: Sort in descending order if True
        locale_name: Locale for string sorting (e.g., 'fr_FR.UTF-8')
        **options: Additional type-specific options

    Returns:
        SortKey object for use in sorting functions

    Example:
        >>> key_spec = key("price", "num", desc=True)
        >>> key_spec = key("name", "str", locale_name="fr_FR.UTF-8")
    """
    return SortKey(
        column=column,
        data_type=data_type,
        desc=desc,
        locale_name=locale_name,
        options=options,
    )


def _extract_value(item: Any, column: Union[str, int]) -> Any:
    """Extract a value from an item using column name or index."""
    if isinstance(item, dict):
        return item.get(column, "")
    elif isinstance(item, (list, tuple)) and isinstance(column, int):
        return item[column] if 0 <= column < len(item) else ""
    else:
        return str(item)


def _convert_value(
    value: Any, data_type: str, locale_name: Optional[str] = None
) -> Any:
    """Convert a value to the appropriate type for sorting."""
    if value is None or value == "":
        # Handle empty values - they sort first
        if data_type == "num":
            return float("-inf")
        elif data_type == "date":
            return date_parser.parse("1900-01-01")
        else:
            return ""

    try:
        if data_type == "num":
            # Try int first, then float
            str_val = str(value).strip()
            if "." in str_val or "e" in str_val.lower():
                return float(str_val)
            else:
                return int(str_val)
        elif data_type == "date":
            if isinstance(value, str):
                return date_parser.parse(value)
            return value
        elif data_type in ("str", "nat"):
            return str(value)
        else:
            return str(value)
    except (ValueError, TypeError):
        # If conversion fails, return a default value
        if data_type == "num":
            return float("-inf")
        elif data_type == "date":
            return date_parser.parse("1900-01-01")
        else:
            return str(value)


def _create_sort_function(keys: List[SortKey]) -> Callable[[Any], tuple]:
    """Create a sorting key function for multiple sort keys."""

    def sort_key_func(item: Any) -> tuple:
        result = []
        for sort_key in keys:
            value = _extract_value(item, sort_key.column)
            converted = _convert_value(value, sort_key.data_type, sort_key.locale_name)

            # Handle natural sorting
            if sort_key.data_type == "nat":
                # For natural sorting, we use natsort but need to handle desc
                nat_key = natsorted([str(converted)], alg=ns.IGNORECASE)[0]
                converted = nat_key

            # Handle locale-specific string sorting
            elif sort_key.data_type == "str" and sort_key.locale_name:
                try:
                    locale.setlocale(locale.LC_COLLATE, sort_key.locale_name)
                    converted = locale.strxfrm(str(converted))
                except locale.Error:
                    # Fall back to regular string sorting if locale not available
                    converted = str(converted).lower()
            elif sort_key.data_type == "str":
                converted = str(converted).lower()

            # Handle descending order by negating numbers or reversing strings
            if sort_key.desc:
                if isinstance(converted, (int, float)):
                    converted = -converted
                elif hasattr(converted, "__reversed__"):
                    # For strings, we'll use a custom comparator approach
                    # This is a simple approach - for better locale support,
                    # we'd need more sophisticated handling
                    pass

            result.append(converted)

        return tuple(result)

    return sort_key_func


def sort_iter(
    data: Iterator[Any],
    keys: List[SortKey],
    stable: bool = True,
    reverse: bool = False,
    unique: Optional[str] = None,
) -> Iterator[Any]:
    """
    Sort an iterator of data in memory.

    Args:
        data: Iterator of items to sort
        keys: List of SortKey specifications
        stable: Use stable sorting algorithm
        reverse: Reverse the entire sort order
        unique: Column name for uniqueness constraint

    Yields:
        Sorted items

    Example:
        >>> data = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
        >>> sorted_data = sort_iter(data, keys=[key("age", "num")])
        >>> list(sorted_data)
        [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    """
    # Convert iterator to list for sorting
    items = list(data)

    # Apply uniqueness constraint if specified
    if unique:
        seen = set()
        unique_items = []
        for item in items:
            unique_val = _extract_value(item, unique)
            if unique_val not in seen:
                seen.add(unique_val)
                unique_items.append(item)
        items = unique_items

    # Create sort function
    sort_func = _create_sort_function(keys)

    # Sort using appropriate algorithm
    if stable:
        sorted_items = sorted(items, key=sort_func, reverse=reverse)
    else:
        # For unstable sort, we can use the same function but note that
        # Python's sort is actually always stable, so this is mainly for API completeness
        sorted_items = sorted(items, key=sort_func, reverse=reverse)

    return iter(sorted_items)


def _chunk_file(
    input_path: Path,
    chunk_size: int,
    keys: List[SortKey],
    temp_dir: Path,
) -> List[Path]:
    """Split a large file into sorted chunks."""
    chunk_files = []
    chunk_num = 0

    file_format = detect_format(input_path)

    with parse_file(input_path) as reader:
        current_chunk = []
        current_size = 0

        for item in reader:
            current_chunk.append(item)
            # Rough estimate of memory usage
            current_size += len(str(item))

            if current_size >= chunk_size:
                # Sort chunk and write to temp file
                sorted_chunk = list(sort_iter(current_chunk, keys))

                chunk_file = temp_dir / f"chunk_{chunk_num:06d}.{file_format}"
                write_file(chunk_file, sorted_chunk, file_format)
                chunk_files.append(chunk_file)

                current_chunk = []
                current_size = 0
                chunk_num += 1

        # Handle remaining items
        if current_chunk:
            sorted_chunk = list(sort_iter(current_chunk, keys))
            chunk_file = temp_dir / f"chunk_{chunk_num:06d}.{file_format}"
            write_file(chunk_file, sorted_chunk, file_format)
            chunk_files.append(chunk_file)

    return chunk_files


def _merge_chunks(
    chunk_files: List[Path],
    output_path: Path,
    keys: List[SortKey],
    unique: Optional[str] = None,
) -> None:
    """Merge sorted chunks using k-way merge."""
    file_format = detect_format(output_path)
    sort_func = _create_sort_function(keys)

    # Open all chunk files
    readers = []
    heap = []

    try:
        for i, chunk_file in enumerate(chunk_files):
            reader = parse_file(chunk_file)
            readers.append(reader)

            # Get first item from each chunk
            try:
                first_item = next(iter(reader))
                heapq.heappush(heap, (sort_func(first_item), i, first_item))
            except StopIteration:
                pass

        # Set for uniqueness constraint
        seen = set() if unique else None

        # Merge and write
        with open(output_path, "w", encoding="utf-8") as output_file:
            writer_func = _get_writer_func(output_file, file_format)

            while heap:
                sort_key_val, chunk_idx, item = heapq.heappop(heap)

                # Check uniqueness constraint
                if unique:
                    unique_val = _extract_value(item, unique)
                    if unique_val in seen:
                        # Skip duplicate, get next item from same chunk
                        try:
                            next_item = next(readers[chunk_idx])
                            heapq.heappush(
                                heap, (sort_func(next_item), chunk_idx, next_item)
                            )
                        except StopIteration:
                            pass
                        continue
                    seen.add(unique_val)

                writer_func(item)

                # Get next item from the same chunk
                try:
                    next_item = next(readers[chunk_idx])
                    heapq.heappush(heap, (sort_func(next_item), chunk_idx, next_item))
                except StopIteration:
                    pass

    finally:
        # Close all readers
        for reader in readers:
            if hasattr(reader, "close"):
                reader.close()


def _get_writer_func(file_obj, file_format: str) -> Callable:
    """Get appropriate writer function for file format."""
    import json

    if file_format == "jsonl":

        def write_jsonl(item):
            file_obj.write(json.dumps(item, ensure_ascii=False) + "\n")

        return write_jsonl
    elif file_format in ("csv", "tsv"):

        def write_csv(item):
            if isinstance(item, dict):
                # For CSV, we'd need to handle headers properly
                # This is a simplified version
                values = list(item.values())
                file_obj.write(",".join(str(v) for v in values) + "\n")
            else:
                file_obj.write(str(item) + "\n")

        return write_csv
    else:  # txt

        def write_txt(item):
            file_obj.write(str(item) + "\n")

        return write_txt


def sort_file(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    keys: List[SortKey],
    memory_limit: Optional[str] = None,
    stable: bool = True,
    reverse: bool = False,
    unique: Optional[str] = None,
    stats: bool = False,
) -> Optional[SortStats]:
    """
    Sort a file and write results to another file.

    Args:
        input_path: Path to input file
        output_path: Path to output file
        keys: List of SortKey specifications
        memory_limit: Memory limit (e.g., '512M', '2G') for external sorting
        stable: Use stable sorting algorithm
        reverse: Reverse the entire sort order
        unique: Column name for uniqueness constraint
        stats: Return sorting statistics

    Returns:
        SortStats object if stats=True, None otherwise

    Example:
        >>> sort_file("data.jsonl", "sorted.jsonl", keys=[key("timestamp", "date")])
    """
    import time

    start_time = time.time()
    input_path = Path(input_path)
    output_path = Path(output_path)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get file size
    file_size = input_path.stat().st_size

    # Determine if we need external sorting
    if memory_limit:
        max_memory = parse_memory_size(memory_limit)
        need_external_sort = file_size > max_memory
    else:
        # Default: use external sort for files > 100MB
        need_external_sort = file_size > 100 * 1024 * 1024

    lines_processed = 0

    if need_external_sort:
        # External sorting for large files
        chunk_size = (
            parse_memory_size(memory_limit) if memory_limit else 50 * 1024 * 1024
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Split into chunks
            chunk_files = _chunk_file(input_path, chunk_size, keys, temp_path)

            # Merge chunks
            _merge_chunks(chunk_files, output_path, keys, unique)
    else:
        # In-memory sorting for smaller files
        with parse_file(input_path) as reader:
            data = list(reader)
            lines_processed = len(data)

            sorted_data = list(
                sort_iter(data, keys, stable=stable, reverse=reverse, unique=unique)
            )

            file_format = detect_format(output_path)
            write_file(output_path, sorted_data, file_format)

    if stats:
        end_time = time.time()
        return SortStats(
            input_file=str(input_path),
            output_file=str(output_path),
            lines_processed=lines_processed,
            processing_time=end_time - start_time,
            input_size=file_size,
            output_size=output_path.stat().st_size,
            external_sort_used=need_external_sort,
        )

    return None
