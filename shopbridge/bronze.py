"""Land source CSVs into bronze. No cleaning."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd

from shopbridge.config import RAW_DIR, SCHEMA_NAME, SOURCE_FILES, WAREHOUSE_DIR, WAREHOUSE_PATH


def _read_csv(path: Path) -> pd.DataFrame:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not read {path} with utf-8, utf-8-sig, or latin-1")


def load_bronze(logical_date: date, raw_dir: Path | None = None) -> dict[str, int]:
    """Copy each source CSV into shopbridge_dev.bronze_* for this logical_date.

    Source is a snapshot: each run restates bronze for that date from the same
    files. A second run deletes the old slice first so rows do not double.
    """
    source_dir = raw_dir if raw_dir is not None else RAW_DIR
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    ingestion_ts = datetime.now(timezone.utc)
    counts: dict[str, int] = {}

    connection = duckdb.connect(str(WAREHOUSE_PATH))
    try:
        connection.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
        for entity, filename in SOURCE_FILES.items():
            path = source_dir / filename
            if not path.is_file():
                raise FileNotFoundError(f"Missing source file: {path}")

            frame = _read_csv(path)
            frame["ingestion_ts"] = ingestion_ts
            frame["source_file_name"] = filename
            frame["logical_date"] = logical_date

            table = f"bronze_{entity}"
            qualified = f"{SCHEMA_NAME}.{table}"
            connection.register("bronze_batch", frame)
            connection.execute(
                f"CREATE TABLE IF NOT EXISTS {qualified} AS SELECT * FROM bronze_batch LIMIT 0"
            )
            connection.execute(
                f"DELETE FROM {qualified} WHERE logical_date = ?",
                [logical_date],
            )
            connection.execute(f"INSERT INTO {qualified} SELECT * FROM bronze_batch")
            connection.unregister("bronze_batch")
            counts[table] = len(frame)
    finally:
        connection.close()

    return counts
