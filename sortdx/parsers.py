"""
File format parsers for sortx.

This module handles reading and writing various file formats including
CSV, TSV, JSONL, plain text, and compressed files.
"""

import csv
import gzip
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Union

try:
    import chardet
except ImportError:
    # Fallback for missing chardet
    class CharDet:
        @staticmethod
        def detect(data):
            return {"encoding": "utf-8", "confidence": 0.9}

    chardet = CharDet()

# Handle optional zstandard dependency
try:
    import zstandard as zstd

    ZSTD_AVAILABLE = True
except ImportError:
    ZSTD_AVAILABLE = False


def detect_format(file_path: Union[str, Path]) -> str:
    """
    Detect file format based on extension.

    Args:
        file_path: Path to the file

    Returns:
        Detected format: 'csv', 'tsv', 'jsonl', or 'txt'
    """
    path = Path(file_path)

    # Handle compressed files
    if path.suffix.lower() in (".gz", ".gzip"):
        # Look at the extension before .gz
        path = path.with_suffix("")
    elif path.suffix.lower() in (".zst", ".zstd"):
        # Look at the extension before .zst
        path = path.with_suffix("")

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return "csv"
    elif suffix in (".tsv", ".tab"):
        return "tsv"
    elif suffix in (".jsonl", ".ndjson", ".json"):
        return "jsonl"
    else:
        return "txt"


def detect_encoding(file_path: Path, sample_size: int = 8192) -> str:
    """
    Detect file encoding using chardet.

    Args:
        file_path: Path to the file
        sample_size: Number of bytes to sample for detection

    Returns:
        Detected encoding (defaults to 'utf-8')
    """
    try:
        opener = _get_file_opener(file_path)
        with opener(file_path, "rb") as f:
            sample = f.read(sample_size)

        detection = chardet.detect(sample)
        encoding = detection.get("encoding", "utf-8")

        # Fallback to utf-8 if detection failed or confidence is low
        if not encoding or detection.get("confidence", 0) < 0.7:
            encoding = "utf-8"

        return encoding
    except Exception:
        return "utf-8"


def _get_file_opener(file_path: Path):
    """Get appropriate file opener based on compression."""
    suffix = file_path.suffix.lower()

    if suffix in (".gz", ".gzip"):
        return gzip.open
    elif suffix in (".zst", ".zstd"):
        if not ZSTD_AVAILABLE:
            raise ImportError(
                "zstandard not installed. Install with: pip install zstandard"
            )
        return lambda path, mode: zstd.open(path, mode)
    else:
        return open


def detect_csv_delimiter(file_path: Path, encoding: str = "utf-8") -> str:
    """
    Detect CSV delimiter by analyzing the first few lines.

    Args:
        file_path: Path to CSV file
        encoding: File encoding

    Returns:
        Detected delimiter (default: ',')
    """
    opener = _get_file_opener(file_path)

    try:
        with opener(file_path, "rt", encoding=encoding) as f:
            # Read first few lines for analysis
            sample_lines = []
            for _ in range(5):
                line = f.readline()
                if not line:
                    break
                sample_lines.append(line)

            if not sample_lines:
                return ","

            sample = "".join(sample_lines)

            # Use csv.Sniffer to detect delimiter
            sniffer = csv.Sniffer()
            try:
                dialect = sniffer.sniff(sample, delimiters=",;\t|")
                return dialect.delimiter
            except csv.Error:
                # Fallback to manual detection
                delimiters = [",", ";", "\t", "|"]
                line = sample_lines[0].strip()

                delimiter_counts = {}
                for delim in delimiters:
                    delimiter_counts[delim] = line.count(delim)

                # Return delimiter with highest count
                best_delim = max(delimiter_counts, key=delimiter_counts.get)
                return best_delim if delimiter_counts[best_delim] > 0 else ","

    except Exception:
        return ","


class FileReader:
    """Base class for file readers."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.encoding = detect_encoding(file_path)
        self.opener = _get_file_opener(file_path)
        self._file_handle = None

    def __enter__(self):
        self._file_handle = self.opener(self.file_path, "rt", encoding=self.encoding)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file_handle:
            self._file_handle.close()

    def __iter__(self):
        return self

    def __next__(self):
        raise NotImplementedError


class CSVReader(FileReader):
    """CSV/TSV file reader."""

    def __init__(self, file_path: Path, delimiter: str = None):
        super().__init__(file_path)
        self.delimiter = delimiter or detect_csv_delimiter(file_path, self.encoding)
        self._csv_reader = None
        self._headers = None

    def __enter__(self):
        self._file_handle = self.opener(self.file_path, "rt", encoding=self.encoding)
        self._csv_reader = csv.DictReader(self._file_handle, delimiter=self.delimiter)
        self._headers = self._csv_reader.fieldnames
        return self

    def __next__(self):
        if not self._csv_reader:
            raise StopIteration
        try:
            return next(self._csv_reader)
        except StopIteration:
            raise


class JSONLReader(FileReader):
    """JSONL (JSON Lines) file reader."""

    def __next__(self):
        if not self._file_handle:
            raise StopIteration

        line = self._file_handle.readline()
        if not line:
            raise StopIteration

        try:
            return json.loads(line.strip())
        except json.JSONDecodeError:
            # Skip invalid JSON lines
            return self.__next__()


class TextReader(FileReader):
    """Plain text file reader (line by line)."""

    def __next__(self):
        if not self._file_handle:
            raise StopIteration

        line = self._file_handle.readline()
        if not line:
            raise StopIteration

        return line.strip()


@contextmanager
def parse_file(file_path: Union[str, Path]) -> Iterator[Any]:
    """
    Create appropriate file reader based on format.

    Args:
        file_path: Path to the file

    Yields:
        FileReader instance

    Example:
        >>> with parse_file("data.csv") as reader:
        ...     for row in reader:
        ...         print(row)
    """
    path = Path(file_path)
    file_format = detect_format(path)

    if file_format in ("csv", "tsv"):
        delimiter = "\t" if file_format == "tsv" else None
        with CSVReader(path, delimiter=delimiter) as reader:
            yield reader
    elif file_format == "jsonl":
        with JSONLReader(path) as reader:
            yield reader
    else:  # txt
        with TextReader(path) as reader:
            yield reader


def write_file(
    file_path: Union[str, Path],
    data: Iterator[Any],
    file_format: str = None,
    encoding: str = "utf-8",
) -> None:
    """
    Write data to file in specified format.

    Args:
        file_path: Output file path
        data: Iterator of data items
        file_format: Format to write ('csv', 'tsv', 'jsonl', 'txt')
        encoding: File encoding
    """
    path = Path(file_path)

    if not file_format:
        file_format = detect_format(path)

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    opener = _get_file_opener(path)

    with opener(path, "wt", encoding=encoding) as f:
        if file_format == "jsonl":
            _write_jsonl(f, data)
        elif file_format in ("csv", "tsv"):
            delimiter = "\t" if file_format == "tsv" else ","
            _write_csv(f, data, delimiter)
        else:  # txt
            _write_text(f, data)


def _write_jsonl(file_handle, data: Iterator[Any]) -> None:
    """Write data as JSONL."""
    for item in data:
        json.dump(item, file_handle, ensure_ascii=False)
        file_handle.write("\n")


def _write_csv(file_handle, data: Iterator[Any], delimiter: str = ",") -> None:
    """Write data as CSV."""
    data_list = list(data)
    if not data_list:
        return

    # Determine headers from first item
    first_item = data_list[0]
    if isinstance(first_item, dict):
        headers = list(first_item.keys())
        writer = csv.DictWriter(file_handle, fieldnames=headers, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data_list)
    else:
        # For non-dict items, write as single column
        writer = csv.writer(file_handle, delimiter=delimiter)
        for item in data_list:
            if isinstance(item, (list, tuple)):
                writer.writerow(item)
            else:
                writer.writerow([item])


def _write_text(file_handle, data: Iterator[Any]) -> None:
    """Write data as plain text."""
    for item in data:
        file_handle.write(str(item) + "\n")
