# ShopBridge Analytics Platform — Project Requirements

**Client:** ShopBridge (fictional marketplace)  
**Role you are filling:** Data Engineer (contractor, solo)  
**Document type:** Requirements and acceptance spec (this README is the contract)  
**Version:** 1.0  
**Date:** 27 August 2026  
**Status:** Approved for build — do not start implementation until you have read this entire document

This repository is the delivery vehicle for the work described below. The client will review **this README plus the code and tests in this repo**. If a behaviour is not in this document, it is not required. If it is in this document, it is required.

---

## 1. Who we are and why we are hiring you

ShopBridge is an online marketplace. Sellers list products; customers place orders that may contain multiple items; payments and reviews arrive after the order.

We have been given a **historical extract** of marketplace data (the public Olist Brazilian e-commerce dataset). We need a **trusted, rerunnable analytics lakehouse** so finance and operations can answer questions without querying raw CSVs.

We are **not** hiring you to build a machine-learning model, a customer-facing app, or a pretty dashboard. We are hiring you to own **ingestion, modelling, quality, and operations**.

---

## 2. Business questions the platform must support

Your gold layer must make these questions answerable with SQL (you do not need to ship a BI tool):

1. Revenue and item volume by day, week, and month  
2. Average order value and items per order  
3. Delivery performance: ordered → approved → shipped → delivered (and late vs on-time vs estimated)  
4. Payment mix (credit card, boleto, voucher, etc.) without **double-counting revenue**  
5. Review scores by product category and by seller  
6. Top sellers and top categories by **item-level** GMV (price × quantity, plus freight if you document it)  
7. Customer location (state) as of a given date — **point-in-time**, not only “current”  
8. Orders that never delivered, and items sitting in cancelled/unavailable statuses  

If a table cannot support one of these questions, the model is incomplete.

---

## 3. Source data

| Item | Requirement |
|---|---|
| Dataset | [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) |
| Files | All **nine** CSVs in the standard Olist package, including `product_category_name_translation.csv` |
| License / use | Educational / portfolio; do not claim this is ShopBridge production data in a misleading way. In the README, state: “Demo data: Olist public dataset.” |
| How data enters the repo | **Must not** be committed. Provide a documented download step (script or exact commands). A clean clone + documented download must be enough. |
| Size | Use the full public extract. Do not subsample unless a documented `dev` profile exists **in addition to** a `full` profile. |

You may not invent a different business process than Olist’s (orders → items → payments → reviews). You **may** add derived columns and slowly changing dimensions as specified below.

---

## 4. Constraints (non-negotiable)

1. **Solo delivery.** You design, build, test, and document. No paid contractors.  
2. **Zero spend.** No paid cloud, no paid APIs, no paid warehouses. Allowed: your laptop, Docker Desktop (personal), Databricks **Free Edition**, GitHub public repo and Actions free minutes, DuckDB, Postgres/Spark running locally, Olist/Kaggle public data.  
3. **Reproducible from Git.** A reviewer with the README and a free account (Kaggle and/or Databricks Free Edition) must be able to reproduce bronze → gold.  
4. **English** for README, comments that matter, table/column names, and commit messages.  
5. **No secrets** in Git. No API keys, no `.env` with credentials.  
6. This document is the spec. Do not expand scope to “impress” the client (extra dashboards, extra clouds, extra datasets) unless we issue a change request.

---

## 5. In scope

- Medallion lakehouse: **bronze / silver / gold**  
- Dimensional model (star) for marketplace analytics  
- Incremental, **idempotent** pipeline keyed by a logical date  
- Data quality gates and a **quarantine** path for bad rows  
- Automated tests  
- Orchestration or a documented equivalent (scheduled job **or** a single entry-point CLI that can be scheduled)  
- Repository hygiene and this README kept accurate as you build  
- A short `docs/model.md` (see §12)

## 6. Out of scope

- Tableau / Power BI / Looker as a deliverable  
- Training ML models or deploying an LLM app  
- Real-time streaming (not required for v1)  
- Multi-cloud or production IAM/VPC  
- PII enrichment from external vendors  
- Backfilling “all of Brazil’s economy” or extra public datasets  
- A second warehouse (e.g. Snowflake **and** Databricks)  
- Kubernetes  

A simple SQL file of example questions (`analysis/example_questions.sql`) **is** in scope. A full BI app is not.

---

## 7. Architecture requirements

### 7.1 Layers

| Layer | What it is | What you must guarantee |
|---|---|---|
| **Bronze** | Raw land of source files | Immutable append or date-stamped raw copies. No business cleaning. Preserve source column names (snake_case OK if documented). Include load metadata: `ingestion_ts`, `source_file_name`, `logical_date`. |
| **Silver** | Clean, typed, deduplicated entities | One silver table (or view-backed table) per source entity at **entity grain**. Types enforced. Duplicates on natural keys removed with a documented rule. Invalid rows **do not silently vanish**. |
| **Gold** | Analytics marts | Star schema. Conformed dimensions. Facts at declared grains. Only gold is for the business questions in §2. |

You must be able to **rebuild gold from silver** (and silver from bronze) without rereading tribal knowledge. Bronze is the replay buffer.

### 7.2 Physical platform

Choose **exactly one** primary platform and state it at the top of this README after you decide:

- **Option A:** Databricks Free Edition (Delta tables, Unity Catalog three-level names)  
- **Option B:** Local lakehouse (e.g. DuckDB + Parquet/Delta-equivalent files, or Spark local)

Do not half-implement both. A one-paragraph “why this option” is required.

### 7.3 Naming

- Catalog/schema (or database) names: `shopbridge_dev` for development. If you also have a `shopbridge` / `prod` schema, document how they differ.  
- Tables: `bronze_<entity>`, `silver_<entity>`, gold as `fct_*` and `dim_*` only.  
- No spaces in identifiers.

---

## 8. Data modelling requirements

### 8.1 Mandatory grain declarations

You must write these sentences in `docs/model.md` and implement tables that match them:

| Table | Grain (one row = …) |
|---|---|
| `fct_order_items` | one **order line** (`order_id` + `order_item_id`) |
| `fct_orders` | one **order** (`order_id`) — measures that are order-level only (e.g. delivery timestamps). **Do not** put item price here as if it were unique per order. |
| `fct_payments` | one **payment installment / payment record** as in the source payment table grain |
| `fct_reviews` | one **review** as in the source (document how you handle multiple reviews per order if present) |
| `dim_customer` | one **customer version** (see SCD2) |
| `dim_product` | one product (`product_id`) |
| `dim_seller` | one seller (`seller_id`) |
| `dim_date` | one calendar day |

### 8.2 Measures (additive vs not)

- **GMV / item price / freight** live at **line** grain and are additive across items, products, sellers, and time.  
- **Payment value** lives on `fct_payments`. You must **not** join payments to items in a way that multiplies revenue. Document the approved way to combine “revenue” vs “payment collected.”  
- **Review score** is not additive across items. Do not `SUM(review_score)` as a KPI.  
- Delivery timestamps are **order-level** (use `fct_orders`).

### 8.3 Slowly changing customer dimension (required)

Olist customers are largely a snapshot. The client still requires **SCD Type 2 mechanics** on `dim_customer` so the pattern exists in production code:

- Columns (minimum): `customer_sk` (surrogate), `customer_id` (natural), `customer_unique_id`, location attributes you keep (zip prefix, city, state), `valid_from`, `valid_to`, `is_current`  
- Intervals **half-open**: a new version’s `valid_from` equals the previous `valid_to`. Current row: `valid_to` = `9999-12-31` (or NULL, but pick one and use it everywhere).  
- Facts that need “customer as of order date” must join on `customer_id` **and** `order_purchase_timestamp` (or order date) between `valid_from` and `valid_to`, **or** store `customer_sk` captured at load. Document which.  
- Because the source may not contain real history, you must **simulate at least two versions** for **≥ 20 customers** (e.g. a documented synthetic state change on a `logical_date`). This is a client requirement so we can demo point-in-time joins. Put the simulation in silver/gold generation, not by editing bronze by hand.

### 8.4 Other dimensions

- `dim_product` must include English category (`product_category_name_english`) via the translation file. Unknown/missing category → `'unknown'`, not dropped.  
- `dim_date` must cover at least 2016-01-01 through 2018-12-31 (Olist range) with `year`, `quarter`, `month`, `month_name`, `week`, `day_of_week`, `is_weekend`.  
- Role-playing: order date vs delivered date must both be joinable to `dim_date` (two FKs from `fct_orders`).

### 8.5 Fan-out (explicitly forbidden in gold)

Gold queries for **item GMV** must not inflate when payments or reviews are attached. If you provide a “wide” convenience table, it is **not** the source of truth; stars are.

---

## 9. Pipeline behaviour

### 9.1 Logical date

Every pipeline run is parameterized by `logical_date` (also called `ds`), type `DATE`.

- Bronze files/tables for that run are attributable to `logical_date`.  
- Silver/gold incremental processing uses a documented watermark (e.g. `order_purchase_timestamp` truncated to date).  
- **Re-running the same `logical_date` must leave gold counts unchanged** (idempotent). Prove this in tests or a scripted check.

### 9.2 Incremental vs full

- Default: **incremental** for orders whose purchase date = `logical_date` (or a documented lookback window).  
- Lookback: **7 days** before `logical_date` to catch late status updates (delivered/cancelled after purchase). Document it.  
- Provide a `full-refresh` mode for gold rebuild from silver (operator flag). Full refresh is allowed to be slow; incremental is the daily path.

### 9.3 Late data and status changes

Orders change status over time. Silver/gold must **upsert** on natural keys (`order_id`, `order_id`+`order_item_id`, etc.). Last source state wins, unless you document a better rule.

### 9.4 Quarantine (required)

Rows that fail **blocking** quality rules go to quarantine tables, not into gold.

Minimum quarantine tables:

- `silver_quarantine_order_items`  
- `silver_quarantine_orders`  

Each quarantine row must include: natural key if available, `failed_rule_id`, `failed_rule_description`, `logical_date`, `ingestion_ts`, and the payload (or a pointer to bronze).

**Blocking rules (minimum):**

| ID | Rule |
|---|---|
| `Q-01` | `order_id` is null |
| `Q-02` | `order_item_id` is null on item records |
| `Q-03` | `price` is null or `< 0` on items |
| `Q-04` | `freight_value` is null or `< 0` on items |
| `Q-05` | `order_purchase_timestamp` is null on orders |
| `Q-06` | duplicate natural key in the same batch after your dedup rule — extras go to quarantine, one survivor stays in silver |

**Non-blocking (warn, still load to silver/gold, metric emitted):**

| ID | Rule |
|---|---|
| `W-01` | delivered date before purchase date |
| `W-02` | `payment_value` = 0  
| `W-03` | review score outside 1–5 if present |

Poison rows must **not** fail the entire `logical_date` unless an operator sets `fail_on_quarantine_rate` and the rate exceeds **5%** of that entity’s rows for the date. Default is: load good rows, quarantine bad rows, **emit a metric**.

### 9.5 Idempotency test the client will run

We will:

1. Run the pipeline for `logical_date = 2018-08-01`  
2. Record `COUNT(*)` on `fct_order_items` and a checksum (e.g. `SUM(price)`)  
3. Run the same date again  
4. Expect **identical** counts and checksums  

If this fails, the project is not accepted.

---

## 10. Quality, tests, and observability

### 10.1 Automated tests (required)

Must run in CI (GitHub Actions on the public repo) **or** a documented one-command local equivalent if Actions cannot reach Databricks. Prefer both: unit tests in CI, warehouse tests documented.

Minimum:

- **Schema tests** on gold: `not_null` on all primary/surrogate keys; `unique` on those keys  
- **Relationship tests:** every `fct_order_items.product_id` exists in `dim_product` (orphans = fail)  
- **Accepted values:** `order_status` in the known Olist status set (document the set)  
- **Idempotency test** (§9.5) as an automated script  
- **No-fanout test:** joining `fct_order_items` to `fct_payments` in a naive way is **not** required to pass; instead, a test that `SUM(price)` on items **equals** a documented GMV definition and does **not** match `SUM(payment_value)` unless you prove they should (they generally should not)

### 10.2 Run metrics (required)

Each successful run must write a `ops_pipeline_run` (name flexible) row or log file with:

- `logical_date`  
- `started_at` / `ended_at` / duration  
- rows in / rows out per layer for orders and items  
- quarantine counts  
- status: `success` / `success_with_warnings` / `failed`  

No paid observability product is required. A table or JSON log is enough.

### 10.3 Freshness (for this historical dataset)

Document: *“This dataset is static; freshness SLA does not apply to source. For a live source we would alert if `max(order_purchase_timestamp)` lagged X.”*  
Still implement a **check** that gold `dim_date` coverage includes all order dates in silver.

---

## 11. How the pipeline is invoked

You must provide **one** supported interface (both if you want, but one is enough):

```text
python -m shopbridge --logical-date 2018-08-01
```

or a Databricks Job / Lakeflow pipeline with a `logical_date` parameter.

Also required:

- `--full-refresh` (or job parameter) to rebuild gold from silver  
- Exit code `0` on success / success_with_warnings; non-zero on failure  
- README section: “How to run a single day” and “How to backfill a date range” (backfill may be a documented loop of daily runs; parallelism is optional)

Retries: document what is safe to retry (the whole date job must be safe).

---

## 12. Documentation you must maintain in this repo

| File | Contents |
|---|---|
| `README.md` | This spec, plus **your** “Implementation notes” section (platform chosen, how to install, how to download data, how to run, how to test). Do not delete the requirements sections. |
| `docs/model.md` | Grains, SCD2, measure additivity, join paths for the eight business questions, fan-out warnings |
| `docs/quality.md` | Rule IDs Q-01… and W-01…, blocking vs warn, quarantine table names |
| `analysis/example_questions.sql` | At least **one SQL query per business question** in §2 (8 queries minimum), each with a one-line comment |

README **Implementation notes** must include:

- Prerequisites (Java, Python version, Databricks account, etc.)  
- Exact commands, copy-pasteable  
- Expected runtime on a laptop or Free Edition (order-of-magnitude is fine, e.g. “full load < 30 minutes”)  
- Known limitations  

---

## 13. Git and engineering standards

- Default branch: `main`  
- Commits: small, present-tense or imperative (“Add silver order dedup”)  
- `.gitignore`: data files, DuckDB, warehouse creds, `__pycache__`, `.venv`, Databricks local caches, `.env`  
- No notebooks as the **only** form of the pipeline. Notebooks are allowed for exploration; production path is modules/jobs/SQL models.  
- Python: 3.11+ if you use Python; pin dependencies (`requirements.txt` or `pyproject.toml`)  
- SQL/dbt models must be readable (CTEs, no 200-line nested soup without structure)  
- Do not commit outputs of runs (parquet dumps, `target/` compiled artifacts except as the tool requires)

**CI (required if the project can run without a paid account):**

- On push to `main` and on pull request: install deps, run unit tests, run dbt tests **or** SQL tests against a small fixture  
- Provide `tests/fixtures/` with a **tiny** fake subset (tens of rows) so CI does not need the full Olist download  

The full Olist download is for local/Databricks demo; CI uses fixtures.

---

## 14. Deliverables checklist (what we will review)

1. Public Git repository (or a private repo you grant us read access to)  
2. This README with Implementation notes filled in  
3. `docs/model.md` and `docs/quality.md`  
4. Working bronze → silver → gold for the full Olist extract  
5. SCD2 demo on customers (§8.3)  
6. Quarantine path with Q-01–Q-06  
7. Idempotent re-run for at least one `logical_date`  
8. Eight example SQL questions  
9. Automated tests + CI or documented equivalent  
10. `ops` run log/metrics  
11. Clean clone instructions that a stranger can follow in under 60 minutes (excluding download time)

---

## 15. Acceptance criteria (pass/fail)

The client will **reject** the delivery if any of the following is true:

- Gold grain does not match §8.1  
- Re-running the same `logical_date` changes `COUNT(*)` or `SUM(price)` on `fct_order_items`  
- Item GMV is implemented in a way that duplicates across payments (fan-out) with no documented separate payment fact  
- Bad prices (`< 0`) appear in `fct_order_items`  
- Source CSVs are committed to Git  
- There is no way to run by `logical_date`  
- `docs/model.md` is missing grain sentences  
- Tests do not exist or cannot be run with a documented command  
- Databricks/cloud credentials or personal tokens are in the repo  

The client will **accept** when:

- All of §14 is present  
- Idempotency check (§9.5) passes  
- Relationship tests pass on gold  
- A reviewer can answer all eight business questions using only gold tables and `analysis/example_questions.sql`  
- README Implementation notes work on a clean environment following Option A or B  

---

## 16. Milestones (suggested; you own the calendar)

These are **client checkpoints**, not a mandate to work in this order, but we will not do a final review until M4 is done.

| Milestone | What we expect to see |
|---|---|
| **M1 — Contract** | Repo created, `.gitignore`, this README copied in, platform option A or B declared |
| **M2 — Bronze** | All nine sources land with load metadata; download script; no data in Git |
| **M3 — Silver** | Typed entities, dedup, Q-01–Q-06 quarantine, lookback upsert documented |
| **M4 — Gold + ops** | Stars, SCD2, eight SQLs, idempotency test, CI, `docs/*`, run metrics |

Do not ask the client to “complete the project” or to pair-program the pipeline. Questions about **this spec** (ambiguity, conflicts) are welcome. Implementation is yours.

---

## 17. Open decisions you must record (not invent silently)

If you choose something the spec allows, write it in Implementation notes:

1. Option A vs Option B  
2. `valid_to` sentinel vs NULL for current SCD2 rows  
3. GMV definition: `price` only vs `price + freight_value`  
4. How multiple payments per order are aggregated for “amount collected”  
5. Timezone: treat all Olist timestamps as naive **UTC-3 (Brazil)** or as naive with **no conversion** — pick one and apply it to all date logic  

If the spec and the source data conflict (e.g. impossible timestamps), use warn rule W-01 and document the row counts. Do not silently drop them from bronze.

---

## 18. Communication protocol

- You implement. The client does **not** provide code, scaffolding, or “sample pipelines” unless you **explicitly ask** for a specific piece of help.  
- When you ask, ask a **narrow** question (e.g. “Does Q-03 apply to freight as well as price?” — already answered: freight is Q-04).  
- Change requests: if you want streaming, RAG, or a dashboard, propose it; default answer is **no** until M4 is accepted.

---

## 19. Implementation notes

*(Contractor: fill this section as you build. Do not remove sections 1–18.)*

**Platform:** _Option A / Option B — TBD_  

**How to download data:** _TBD_  

**How to run one day:** _TBD_  

**How to run tests:** _TBD_  

**GMV definition:** _TBD_  

**SCD2 current-row convention:** _TBD_  

**Timezone convention:** _TBD_  

---

*End of requirements. ShopBridge Analytics Platform v1.0.*
