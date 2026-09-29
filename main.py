"""
Sunday Market Recap — Data Puller
CLI entry point.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.config.loader import load_config
from src.clients.massive import MassiveClient
from src.pipelines.puller import DataPuller
from src.utils.logging import setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sunday Market Recap — Data Puller")
    parser.add_argument("--start", type=date.fromisoformat, default=None)
    parser.add_argument("--end", type=date.fromisoformat, default=None)
    parser.add_argument("--group", type=str, default=None)
    parser.add_argument("--symbol", type=str, default=None)
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--list-groups", action="store_true")
    parser.add_argument("--log-dir", type=Path, default=Path("./logs"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(log_dir=args.log_dir)

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.list_groups:
        from src.config.symbols import SymbolRegistry
        registry = SymbolRegistry(config)
        print(f"\nConfigured provider: {config.provider}")
        print(f"Output directory:    {config.output_dir}\n")
        for group in registry.groups():
            entries = registry.for_group(group)
            print(f"  [{group}]")
            for e in entries:
                sym_info = (
                    f"{e.canonical}"
                    + (f" → {e.provider_symbol}" if e.provider_symbol != e.canonical else "")
                    + (f" ({e.currency})" if e.currency else "")
                )
                print(f"    {sym_info}")
        return

    if config.provider == "massive":
        try:
            client = MassiveClient(api_key=config.api_key)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"ERROR: Unsupported provider '{config.provider}'.", file=sys.stderr)
        sys.exit(1)

    puller = DataPuller(config=config, client=client)
    try:
        summary = puller.run(
            start=args.start,
            end=args.end,
            group=args.group,
            symbol=args.symbol,
        )
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if summary.get("failed", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
