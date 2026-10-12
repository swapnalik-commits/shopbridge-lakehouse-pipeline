"""CLI: python -m shopbridge --logical-date YYYY-MM-DD"""

from __future__ import annotations

import argparse
from datetime import date


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="shopbridge")
    parser.add_argument("--logical-date", required=True, help="Run date, YYYY-MM-DD")
    parser.add_argument(
        "--full-refresh",
        action="store_true",
        help="Rebuild gold from silver",
    )
    parser.add_argument(
        "--fail-on-quarantine-rate",
        action="store_true",
        help="Fail the run if quarantine exceeds 5 percent (off by default)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    from shopbridge.bronze import load_bronze

    args = parse_args(argv)
    logical_date = date.fromisoformat(args.logical_date)
    print(f"logical_date={logical_date.isoformat()} full_refresh={args.full_refresh}")
    counts = load_bronze(logical_date)
    for table, n_rows in counts.items():
        print(f"{table}: {n_rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
