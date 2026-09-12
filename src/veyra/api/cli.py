"""Command line interface for Veyra."""

import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import veyra
from veyra.core.config import get_settings
from veyra.infrastructure.assets.local import LocalAssetStore
from veyra.infrastructure.database.sqlite import SQLiteDatabase


def run_health_check() -> int:
    """Perform health checks on foundational components and print status."""
    console = Console()
    settings = get_settings()

    db_path = settings.resolved_database_path()
    db = SQLiteDatabase(db_path)
    db_ok = db.ping()

    asset_path = settings.resolved_asset_dir()
    asset_store = LocalAssetStore(asset_path)
    asset_ok = asset_store.base_path.exists() and asset_store.base_path.is_dir()

    embedding_path = settings.base_dir / settings.embedding_storage_dir
    embedding_path.mkdir(parents=True, exist_ok=True)
    embedding_ok = embedding_path.exists()

    all_ok = db_ok and asset_ok and embedding_ok

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row("Version:", f"[cyan]{veyra.__version__}[/cyan]")
    table.add_row("Environment:", f"[green]{settings.env}[/green]")
    table.add_row("Debug:", f"{'[yellow]True[/yellow]' if settings.debug else 'False'}")
    table.add_row("", "")
    table.add_row(
        "Persistence (SQLite):",
        "[green]READY[/green]" if db_ok else "[red]FAILED[/red]",
    )
    table.add_row(
        "Asset Store (Local):",
        "[green]READY[/green]" if asset_ok else "[red]FAILED[/red]",
    )
    table.add_row(
        "Embedding Store (Local/NumPy):",
        "[green]READY[/green]" if embedding_ok else "[red]FAILED[/red]",
    )
    table.add_row("", "")
    table.add_row(
        "Overall Status:",
        "[bold green]READY[/bold green]" if all_ok else "[bold red]NOT READY[/bold red]",
    )

    panel = Panel(
        table,
        title="[bold blue]VEYRA[/bold blue]",
        subtitle="[dim]Visual Identity Intelligence Platform[/dim]",
        expand=False,
        border_style="blue",
    )
    console.print(panel)

    return 0 if all_ok else 1


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="veyra",
        description="Project Veyra CLI",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("health", help="Run environment and infrastructure health check")
    subparsers.add_parser("version", help="Show Veyra version")

    args = parser.parse_args()

    if args.command == "health" or args.command is None:
        exit_code = run_health_check()
        sys.exit(exit_code)
    elif args.command == "version":
        print(f"Veyra v{veyra.__version__}")
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
