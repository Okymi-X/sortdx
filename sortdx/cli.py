"""
Command-line interface for sortdx.

This module provides the CLI using Typer for a modern command-line experience
with rich help formatting and validation.
"""

import sys
from pathlib import Path
from typing import List, Optional

try:
    import typer
    from rich.console import Console
    from rich.table import Table

    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False

    # Fallback for missing typer/rich
    class Console:
        def print(self, *args, **kwargs):
            print(*args)

    console = Console()

from .core import sort_iter
from .utils import SortKey, parse_key_spec

if TYPER_AVAILABLE:
    from .core import sort_file
    from .utils import parse_memory_size, validate_sort_keys

    # Create Typer app
    app = typer.Typer(
        name="sortdx",
        help="Universal sorting tool for files and data structures",
        add_completion=False,
    )

    # Rich console for pretty output
    console = Console()


def basic_sort(data, args):
    """
    Basic sort function for testing and simple operations.

    Args:
        data: List of items to sort
        args: Object with sorting configuration (keys, reverse, etc.)

    Returns:
        List of sorted items
    """
    # Parse sort keys
    sort_keys = []
    for key_spec in args.keys:
        sort_keys.append(parse_key_spec(key_spec))

    # Use sort_iter for the actual sorting
    sorted_iter = sort_iter(
        data=iter(data),
        keys=sort_keys,
        stable=True,
        reverse=args.reverse,
        unique=getattr(args, "unique", None),
    )

    return list(sorted_iter)


def main():
    """Simple fallback main function."""
    if not TYPER_AVAILABLE:
        print("sortdx CLI requires additional dependencies.")
        print("Install with: pip install sortdx[full]")
        return

    # The actual typer app main function will be defined below
    app()


if TYPER_AVAILABLE:

    def _validate_inputs(input_file: str, memory_limit: Optional[str]) -> None:
        """Validate CLI inputs."""
        # Validate input file
        input_path = Path(input_file)
        if not input_path.exists():
            console.print(f"[red]Error:[/red] Input file '{input_file}' not found")
            raise typer.Exit(1)

        # Validate memory limit format
        if memory_limit:
            try:
                parse_memory_size(memory_limit)
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)


def _parse_sort_keys(
    keys: List[str], locale: Optional[str], natural: bool
) -> List[SortKey]:
    """Parse and validate sort keys."""
    try:
        sort_keys = []

        # If no keys specified, use default behavior
        if not keys:
            if natural:
                sort_keys = [SortKey(column=0, data_type="nat")]
            else:
                sort_keys = [SortKey(column=0, data_type="str")]
        else:
            for key_spec in keys:
                key = parse_key_spec(key_spec)

                # Apply global options
                if locale and key.data_type == "str" and not key.locale_name:
                    key.locale_name = locale

                if natural and key.data_type == "str":
                    key.data_type = "nat"

                sort_keys.append(key)

        validate_sort_keys(sort_keys)
        return sort_keys

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _display_operation_summary(
    input_file: str,
    output: str,
    sort_keys: List[SortKey],
    memory_limit: Optional[str],
) -> None:
    """Display a summary of the sorting operation."""
    console.print("\n[bold]Sorting Operation Summary[/bold]")

    table = Table(show_header=False, box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    table.add_row("Input file", input_file)
    table.add_row("Output file", output if output != "-" else "stdout")

    # Format sort keys
    key_descriptions = []
    for key in sort_keys:
        desc = f"{key.column}:{key.data_type}"
        if key.desc:
            desc += ":desc"
        if key.locale_name:
            desc += f":locale={key.locale_name}"
        key_descriptions.append(desc)

    table.add_row("Sort keys", ", ".join(key_descriptions))

    if memory_limit:
        table.add_row("Memory limit", memory_limit)

    console.print(table)
    console.print()


@app.command()
def main(
    input_file: str = typer.Argument(..., help="Input file path", metavar="INPUT"),
    output: Optional[str] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output file path (default: stdout)",
        metavar="FILE",
    ),
    keys: List[str] = typer.Option(
        [],
        "-k",
        "--key",
        help="Sort key specification (format: column:type[:options])",
        metavar="KEY_SPEC",
    ),
    reverse: bool = typer.Option(False, "--reverse", help="Sort in descending order"),
    stable: bool = typer.Option(
        True, "--stable/--unstable", help="Use stable sorting algorithm"
    ),
    unique: Optional[str] = typer.Option(
        None, "--unique", help="Column name for uniqueness constraint", metavar="COLUMN"
    ),
    locale: Optional[str] = typer.Option(
        None,
        "--locale",
        help="Locale for string sorting (e.g., fr_FR.UTF-8)",
        metavar="LOCALE",
    ),
    memory_limit: Optional[str] = typer.Option(
        None,
        "--memory-limit",
        help="Memory limit for external sorting (e.g., 512M, 2G)",
        metavar="SIZE",
    ),
    natural: bool = typer.Option(
        False, "--natural", help="Use natural sorting for all string columns"
    ),
    stats: bool = typer.Option(False, "--stats", help="Show sorting statistics"),
    version: bool = typer.Option(False, "--version", help="Show version information"),
) -> None:
    """
    Sort files and data structures with support for multiple formats and large datasets.

    EXAMPLES:

    Sort CSV by price (numeric), then name (string):
        sortdx data.csv -o sorted.csv -k price:num -k name:str

    Sort JSONL by timestamp with memory limit:
        sortdx logs.jsonl.gz -o sorted.jsonl.gz -k timestamp:date --memory-limit=512M

    Natural sort of text file:
        sortdx filenames.txt -o sorted.txt --natural

    Sort with uniqueness constraint:
        sortdx users.jsonl -o unique.jsonl -k created_at:date --unique=id
    """
    # Handle version flag
    if version:
        from . import __version__

        console.print(f"sortdx version {__version__}")
        raise typer.Exit()

    # Validate inputs
    _validate_inputs(input_file, memory_limit)

    # Set default output to stdout if not specified
    if not output:
        output = "-"  # stdout

    # Parse and validate sort keys
    sort_keys = _parse_sort_keys(keys, locale, natural)

    # Display operation summary if stats requested
    if stats:
        _display_operation_summary(input_file, output, sort_keys, memory_limit)

    # Perform sorting
    try:
        if output == "-":
            # Output to stdout
            console.print("[yellow]Warning:[/yellow] Stdout output not yet implemented")
            console.print("Please specify an output file with -o/--output")
            raise typer.Exit(1)
        else:
            # Sort to file
            result_stats = sort_file(
                input_path=input_file,
                output_path=output,
                keys=sort_keys,
                memory_limit=memory_limit,
                stable=stable,
                reverse=reverse,
                unique=unique,
                stats=stats,
            )

            if stats and result_stats:
                console.print("\n" + str(result_stats))
            else:
                console.print(f"[green]✓[/green] Sorted data written to {output}")

    except Exception as e:
        console.print(f"[red]Error:[/red] Sorting failed: {e}")
        if "--debug" in sys.argv:
            import traceback

            traceback.print_exc()
        raise typer.Exit(1)


@app.command(name="examples")
def show_examples() -> None:
    """Show usage examples for sortdx."""
    console.print("\n[bold]sortdx Usage Examples[/bold]\n")

    examples = [
        ("Sort CSV by numeric column", "sortdx sales.csv -o sorted.csv -k revenue:num"),
        (
            "Multi-key sort with locale",
            "sortdx customers.csv -o sorted.csv -k country:str:locale=fr -k name:str",
        ),
        (
            "Sort large JSONL file",
            "sortdx logs.jsonl.gz -o sorted.jsonl.gz -k timestamp:date --memory-limit=1G",
        ),
        ("Natural sort of filenames", "sortdx filenames.txt -o sorted.txt --natural"),
        (
            "Sort with uniqueness",
            "sortdx users.jsonl -o unique.jsonl -k created_at:date --unique=user_id",
        ),
        (
            "Reverse sort by date",
            "sortdx events.jsonl -o sorted.jsonl -k date:date --reverse",
        ),
        (
            "Sort TSV with custom delimiter",
            "sortdx data.tsv -o sorted.tsv -k price:num -k category:str",
        ),
    ]

    for i, (description, command) in enumerate(examples, 1):
        console.print(f"[bold cyan]{i}.[/bold cyan] {description}")
        console.print(f"   [dim]{command}[/dim]\n")


@app.command(name="types")
def show_data_types() -> None:
    """Show available data types for sort keys."""
    console.print("\n[bold]Available Data Types[/bold]\n")

    types_table = Table()
    types_table.add_column("Type", style="cyan")
    types_table.add_column("Description")
    types_table.add_column("Examples")

    types_table.add_row(
        "str", "String/text sorting", "name:str, category:str:locale=fr"
    )
    types_table.add_row("num", "Numeric sorting (int/float)", "price:num, age:num")
    types_table.add_row("date", "Date/time sorting", "created_at:date, timestamp:date")
    types_table.add_row(
        "nat", "Natural sorting (file2 < file10)", "filename:nat, version:nat"
    )

    console.print(types_table)

    console.print("\n[bold]Key Options[/bold]\n")

    options_table = Table()
    options_table.add_column("Option", style="cyan")
    options_table.add_column("Description")
    options_table.add_column("Example")

    options_table.add_row(
        "desc=true", "Sort in descending order", "price:num:desc=true"
    )
    options_table.add_row(
        "locale=LOCALE",
        "Use specific locale for strings",
        "name:str:locale=fr_FR.UTF-8",
    )

    console.print(options_table)


if __name__ == "__main__":
    app()
