"""Download or verify the Olist Brazilian e-commerce CSVs.

Method 1 — browser (simplest):
  1. Free Kaggle account: https://www.kaggle.com/account/login
  2. Dataset: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
  3. Download the zip and unzip the nine CSVs into data/raw/

Method 2 — Kaggle API (optional):
  If the `kaggle` package is installed and kaggle.json lives in
  %USERPROFILE%\\.kaggle\\, this script will try to download automatically.

This script always checks that all nine required files exist.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REQUIRED_FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"


def missing_files() -> list[str]:
    return [name for name in REQUIRED_FILES if not (RAW_DIR / name).is_file()]


def try_kaggle_download() -> None:
    if not missing_files():
        return
    try:
        import kaggle  # noqa: F401
    except ImportError:
        return

    print("Some files are missing. Trying the Kaggle API...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kaggle",
            "datasets",
            "download",
            "-d",
            "olistbr/brazilian-ecommerce",
            "-p",
            str(RAW_DIR),
            "--unzip",
        ],
        check=False,
    )
    if result.returncode != 0:
        print("Kaggle API download failed. Use Method 1 in this file's docstring.")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    try_kaggle_download()

    missing = missing_files()
    if missing:
        print("Missing required files in data/raw/:")
        for name in missing:
            print(f"  - {name}")
        print()
        print("Download them from:")
        print("  https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")
        print("Unzip the nine CSVs into data/raw/ and run this script again.")
        sys.exit(1)

    print("All nine Olist CSVs are present in data/raw/.")
    sys.exit(0)


if __name__ == "__main__":
    main()
