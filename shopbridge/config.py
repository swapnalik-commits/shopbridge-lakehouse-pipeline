"""Project paths and warehouse names. No business logic."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
WAREHOUSE_DIR = DATA_DIR / "warehouse"
WAREHOUSE_PATH = WAREHOUSE_DIR / "shopbridge.duckdb"
SCHEMA_NAME = "shopbridge_dev"

SOURCE_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}
