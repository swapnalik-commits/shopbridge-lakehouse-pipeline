# ShopBridge — Complete End-to-End Build Guide

**Working project root (use this, not Downloads):** `D:\Projects\shopbridge-lakehouse-pipeline`  
**Contract (what you must deliver):** `D:\Projects\shopbridge-lakehouse-pipeline\docs\requirements.md`  
**This file:** how to go from a Windows laptop to a client-accepted lakehouse  
**OS:** Windows 10/11  
**Cost:** $0  

This guide does **not** write the pipeline for you. It tells you the order of work, exact environment setup, what “done” means after each step, and what to try when something fails.

If this guide and `docs\requirements.md` conflict, **the requirements file wins**.

A copy of this playbook also lives in the working repo as `HOW-TO-BUILD.md`. Work only under `D:\Projects\shopbridge-lakehouse-pipeline`.

---

## How to use this document

1. Read **Where you are now**, then **Decision: Option A vs B**.  
2. Work **one phase at a time**. Do not jump to gold.  
3. After each phase, run the **Exit check**. If it fails, use **If this fails** in that phase before continuing.  
4. Record decisions in `docs\requirements.md` §19 as soon as you make them. Also keep the root `README.md` accurate for a stranger who clones the repo.  
5. Commit after every phase that produces files. Small commits.

**Suggested calendar**

| When | Phases |
|---|---|
| This week | 0–3 (setup, hygiene, data check, source study) |
| Next | 4–6 (skeleton, fixtures, bronze) |
| After that | 7–9 (silver, gold, SCD2) |
| Then | 10–13 (ops, tests, docs, full run) |

Do not start Phase 6 until you can write a small Python script and basic SQL.

---

## Where you are now (as of this guide)

Your repo already has some of Milestone **M1** and most of the **data download**:

| Item | Status | What that means |
|---|---|---|
| Git repo at `D:\Projects\shopbridge-lakehouse-pipeline` | Done | Do **not** `git init` again |
| Remote `origin` / `main` | Present | You can push later; do not force-push |
| `docs\requirements.md` | Done | This is the client spec |
| Root `README.md` | Skeleton only | You must fill it before delivery |
| `.gitignore` | Done | Ignores `data/raw/*` and `.env` |
| `.env.example` | Done | Databricks vars; unused if you pick Option B |
| `setup.sh` | Present | Bash script. On Windows you do **not** need to run it |
| `data\raw\` nine Olist CSVs | Present locally | Phase 2 is **verify + download script**, not a new download |
| `shopbridge` package, `requirements.txt`, tests | Missing | You still have to create these |
| Pipeline / gold tables | Not started | Phases 6–10 |

**Do this once before Phase 0 commands:**

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
git status
dir data\raw\*.csv
```

You should see nine CSVs. `git status` should **not** list those CSVs as new files to commit. If it does, stop and fix `.gitignore` (Phase 1.1).

**If `D:\Projects\...` does not exist:** the project is elsewhere. Search Explorer for `shopbridge-lakehouse-pipeline`. If you only have `C:\Users\swapn\Downloads\Job Application\olist-lakehouse`, copy/clone into `D:\Projects\shopbridge-lakehouse-pipeline` first, then continue. Do not build in two folders.

---

## Decision: Option A vs Option B (do this first)

The client allows **exactly one** platform.

| | Option A | Option B (recommended default) |
|---|---|---|
| What | Databricks Free Edition (Delta, Unity Catalog) | Local Python + DuckDB on disk |
| Resume | Stronger for Databricks / Spark / Delta | Strong for SQL, tests, CI |
| CI on GitHub | Harder (warehouse is in the cloud) | Easy (`pytest` on fixtures) |
| Windows pain | Low (browser) | Low (no Spark install) |
| Typical failure | Signup, card prompt, daily quota | Almost none |

**Recommended for you:** **Option B**, unless the 30-minute Databricks spike below succeeds and you specifically want Databricks on the resume.

### 30-minute Databricks spike (optional)

1. Open [Databricks Free Edition signup](https://login.databricks.com/?dbx_source=docs&intent=CE_SIGN_UP).  
2. Sign up with Google, GitHub, or email. **Do not enter a credit card.** If they demand a card, stop. Choose Option B.  
3. Wait until a workspace opens. In the SQL editor run `SELECT 1`.  
4. If that works in 30 minutes, you **may** choose Option A.  
5. If signup hangs, asks for payment, or the workspace never appears: **Option B**. Do not wait days.

Write the choice immediately in `docs\requirements.md` §19:

- Platform: Option A or Option B  
- One sentence why  

Then follow **only** that path. Sections marked **A only** or **B only** apply to that path.

---

# Phase 0 — Machine setup

You need a working Python and Git on Windows. You do **not** need AWS, Azure paid, Java, Hadoop, Spark-on-Windows, Docker, or Kubernetes for v1.

## 0.1 Open the project in Cursor

1. File → Open Folder → `D:\Projects\shopbridge-lakehouse-pipeline`  
2. Open a terminal **inside Cursor** (`` Ctrl+` ``).  
3. Confirm:

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
dir
```

You should see `docs`, `data`, `README.md`, `.gitignore`.

**If Cursor opened the Downloads `olist-lakehouse` folder:** close it and open `D:\Projects\shopbridge-lakehouse-pipeline`. All later commands assume that root.

## 0.2 Tools

| Tool | Why | Check |
|---|---|---|
| Git | Commits / GitHub | `git --version` |
| Python **3.11 or 3.12** | Pipeline | `py -3.11 --version` |
| Cursor or VS Code | Edit | you already have Cursor |
| (Option A) Browser + Free Edition | Compute | workspace URL loads |

### Install Git if missing

1. Download: https://git-scm.com/download/win  
2. Install with defaults. Enable “Git from the command line”.  
3. Close and reopen the terminal (and Cursor).  
4. `git --version`

**If this fails:**

```cmd
winget install Git.Git
```

Then close and reopen Cursor so PATH refreshes.

**If `winget` is not recognized:** use the Git installer from git-scm.com.  
**If Git works in Git Bash but not in Cursor:** restart Cursor after install.

### Install Python 3.11 if missing

1. https://www.python.org/downloads/release/python-3119/ (or any 3.11.x)  
2. On the installer, tick **Add python.exe to PATH** and include **pip**.  
3. Reopen the terminal / Cursor.  
4. Check:

```cmd
py -0p
py -3.11 --version
```

**If `py` is not recognized:** try `python --version`. If that is missing or 2.7, reinstall 3.11 with PATH checked.

**If you only have 3.10:** usable; write 3.10 in the README. Avoid 3.14 until DuckDB/pytest wheels exist for it.

**If the Microsoft Store Python is broken** (`python` opens the Store): uninstall Store Python, install from python.org.

**If two Pythons confuse you:** always create the venv with `py -3.11 -m venv .venv` so the project is pinned.

### Terminal: Command Prompt vs PowerShell

Both work. Commands below show **cmd** first.

| Task | Command Prompt | PowerShell |
|---|---|---|
| Go to project | `cd /d D:\Projects\shopbridge-lakehouse-pipeline` | `cd D:\Projects\shopbridge-lakehouse-pipeline` |
| Activate venv | `.\.venv\Scripts\activate.bat` | `.\.venv\Scripts\Activate.ps1` |

**If PowerShell blocks Activate.ps1:**

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then retry `Activate.ps1`. If you do not want to change policy, use Command Prompt instead (`cmd` in the Cursor terminal dropdown).

**If antivirus locks `.venv` or DuckDB:** add `D:\Projects\shopbridge-lakehouse-pipeline` as an exclusion, or pause real-time scan while creating the venv.

## 0.3 Git identity (only if Git complains later)

```cmd
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use your real GitHub email. Do not invent a company email.

## 0.4 Cursor Python interpreter (after Phase 1 venv exists)

1. `Ctrl+Shift+P` → **Python: Select Interpreter**  
2. Choose `D:\Projects\shopbridge-lakehouse-pipeline\.venv\Scripts\python.exe`  
3. New terminals should show `(.venv)` in the prompt.

**If the interpreter list is empty:** create the venv first (Phase 1.2), then retry.

## 0.5 Phase 0 exit check

- [ ] Cursor folder is `D:\Projects\shopbridge-lakehouse-pipeline`  
- [ ] `git --version` prints a version  
- [ ] `py -3.11 --version` or `python --version` is 3.11/3.12  
- [ ] Option A or B written in `docs\requirements.md` §19  

---

# Phase 1 — Repo hygiene (finish M1)

Git already exists. You are tightening the repo, not starting over.

## 1.1 Confirm `.gitignore`

Open `.gitignore`. It must ignore at least:

- `.env`  
- `data/raw/*`, `data/bronze/*`, `data/silver/*`, `data/gold/*`  
- `.venv/`, `__pycache__/`

**Add these lines if they are missing** (recommended):

```gitignore
*.csv
*.parquet
*.duckdb
*.wal
.pytest_cache/
kaggle.json
*.log
*.egg-info/
data/warehouse/*
!data/warehouse/.gitkeep
```

Keep the `!data/raw/.gitkeep` exceptions so empty folders stay in Git.

**If `git status` shows Olist CSVs:**

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
git rm -r --cached data\raw
git status
```

Then commit the ignore fix. The files stay on disk; they leave the index.

**If you accidentally committed CSVs already:**

```cmd
git rm -r --cached data\raw
git commit -m "Stop tracking Olist CSVs"
```

If they were already pushed to GitHub, the files remain in history. For a portfolio this is bad. Prefer a fresh public repo later; do not `git push --force` on `main` unless you know why.

## 1.2 Virtual environment

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
py -3.11 -m venv .venv
.\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
```

PowerShell:

```powershell
cd D:\Projects\shopbridge-lakehouse-pipeline
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

**If `venv` fails with ensurepip:** reinstall Python 3.11 with pip ticked.

**If activate cannot find the script:** the venv did not create. Delete the `.venv` folder in Explorer and rerun `py -3.11 -m venv .venv`.

**If Windows reports a long-path error:** enable long paths, or keep the project at `D:\Projects\shopbridge-lakehouse-pipeline` (already short enough).

Create `requirements.txt` in the project root (Option B starter):

```text
duckdb>=1.1.0
pandas>=2.2.0
pyarrow>=17.0.0
pytest>=8.0.0
python-dateutil>=2.9.0
```

Then:

```cmd
pip install -r requirements.txt
```

**If pip fails (SSL / proxy / corporate VPN):**

```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

If still failing: disconnect VPN, or use a phone hotspot, then retry.

**If `pip` is not recognized:** you forgot to activate the venv, or you are using the wrong Python. The prompt should start with `(.venv)`.

**Option A:** do not install Databricks Connect yet. Build first in the browser notebook / SQL editor. Laptop packages can stay as pytest-only until you need them.

## 1.3 Do not run `setup.sh` on Windows

`setup.sh` is a Linux/macOS helper. It would **overwrite** `README.md` and `.gitignore`. You already have those. **Skip it.** Create folders yourself in Phase 4.

**If you already ran it by accident:** `git status` and `git checkout -- README.md .gitignore` if Git still has the previous versions. Recreate `.gitkeep` files if data folders vanished.

## 1.4 First hygiene commit

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
git add .gitignore requirements.txt HOW-TO-BUILD.md
git status
git commit -m "Add Python deps and build guide"
```

Do **not** `git add .` until you have confirmed CSVs are not staged.

## 1.5 Phase 1 exit check

- [ ] `.venv` exists and is **not** in `git status`  
- [ ] `pip show duckdb` works with venv active (Option B)  
- [ ] Nine CSVs are on disk and **not** staged  
- [ ] At least one new commit after this phase  

---

# Phase 2 — Source data (verify + download script)

You already have the nine files. The client still requires a **documented download step** so a stranger can reproduce.

## 2.1 Verify the nine files

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
dir data\raw\*.csv
```

Required names:

- `olist_customers_dataset.csv`  
- `olist_geolocation_dataset.csv`  
- `olist_orders_dataset.csv`  
- `olist_order_items_dataset.csv`  
- `olist_order_payments_dataset.csv`  
- `olist_order_reviews_dataset.csv`  
- `olist_products_dataset.csv`  
- `olist_sellers_dataset.csv`  
- `product_category_name_translation.csv`  

**If a file is missing:** unzip again. Sometimes Kaggle puts files in a subfolder. Move the nine CSVs up into `data\raw\`.

**If you have extra files** (zip, `__MACOSX`): leave them out of Git; you can delete the zip to save disk.

## 2.2 If you ever need to re-download

Try in this order.

### Method 1 — Browser (simplest)

1. Free Kaggle account: https://www.kaggle.com/account/login  
2. https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce  
3. Download the zip.  
4. Unzip into `D:\Projects\shopbridge-lakehouse-pipeline\data\raw\`  

**If Download is greyed out:** accept dataset terms / join Kaggle, retry.  
**If phone verification is required:** complete it (still free) or use Method 3.

### Method 2 — Kaggle API

1. Kaggle → Account → Create New Token → `kaggle.json`.  
2. Put it **outside** the repo:

```cmd
mkdir "%USERPROFILE%\.kaggle"
copy "%USERPROFILE%\Downloads\kaggle.json" "%USERPROFILE%\.kaggle\kaggle.json"
```

3. Never commit `kaggle.json`.

```cmd
pip install kaggle
python -m kaggle datasets download -d olistbr/brazilian-ecommerce -p data\raw --unzip
```

**If 401/403:** recreate the token. File must contain `username` and `key`.  
**If `kaggle` is not recognized:** use `python -m kaggle ...` as above.

### Method 3 — Copy the zip from another machine

Same nine CSVs in `data\raw\`.

## 2.3 Write `scripts\download_data.py` (required)

Create folder `scripts`. The script should:

- Create `data\raw` if missing  
- Explain Method 1 in a docstring  
- Try Method 2 if `kaggle` is available  
- Exit non-zero with a clear message if any of the nine files is missing  

Then fill `docs\requirements.md` §19 **How to download data** with the exact commands you used.

## 2.4 Phase 2 exit check

- [ ] Nine CSVs in `data\raw\`  
- [ ] `git status` does not list them  
- [ ] `scripts\download_data.py` exists  
- [ ] Download steps written in §19  

---

# Phase 3 — Learn the source (no cleaning)

Spend 2–4 hours. Use Python, Excel, or DuckDB. **Do not change the CSVs.**

For each file, write in a personal note (later `docs\model.md`):

- Grain: what is one row?  
- Natural key  
- How it joins to orders  
- Junk you saw (negative price, empty `order_id`)

Facts you must internalize:

| Entity | Grain | Why it matters |
|---|---|---|
| Orders | one `order_id` | Status and delivery timestamps live here |
| Items | one `order_id` + `order_item_id` | This is gold `fct_order_items` |
| Payments | one payment row per order (often + `payment_sequential`) | Never join this onto items for GMV |
| Reviews | one review | Scores are not additive like money |
| Customers | `customer_id` (also `customer_unique_id`) | SCD2 goes here |
| Products / sellers | `product_id` / `seller_id` | Dimensions |
| Geolocation | zip-level, huge | Land in bronze. You may skip it in gold if city/state already sit on customers/sellers. Client did not require a geo fact. |

List distinct `order_status` values. You will put that set in `docs\quality.md`.

Quick peek (Option B, venv on):

```cmd
python -c "import pandas as pd; o=pd.read_csv(r'data/raw/olist_orders_dataset.csv'); print(o['order_status'].value_counts()); print(o.columns.tolist())"
```

**If this is slow:** that is fine. Do not load geolocation into Excel if Excel chokes; use Python `head` / `value_counts` only.

**If MemoryError:** you tried to open geolocation in Excel. Use Python only for that file.

## 3.1 Phase 3 exit check

- [ ] You can say item vs order vs payment grain in one sentence each  
- [ ] You have the `order_status` value list  
- [ ] You know why payments must not join to items for revenue  

---

# Phase 4 — Project skeleton (still no business logic)

## 4.1 Create folders

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
mkdir shopbridge scripts tests\fixtures analysis data\warehouse
mkdir src\extract src\transform src\load
```

`docs` already exists. That is fine.

Suggested layout (Option B):

```text
D:\Projects\shopbridge-lakehouse-pipeline\
  README.md
  HOW-TO-BUILD.md
  docs\requirements.md
  docs\model.md
  docs\quality.md
  requirements.txt
  .gitignore
  shopbridge\
    __init__.py
    __main__.py          # CLI: --logical-date, --full-refresh
    config.py            # paths, schema shopbridge_dev
    bronze.py
    silver.py
    gold.py
    quality.py
    ops.py
  scripts\
    download_data.py
  tests\
    fixtures\
    test_quality.py
    test_idempotency.py
    test_grain.py
  analysis\
    example_questions.sql
  data\                    # gitignored contents
    raw\
    bronze\
    silver\
    gold\
    warehouse\             # DuckDB file
```

**Option A:** same module names; tables live in Unity Catalog `shopbridge_dev`.

You may use `src\extract` etc. **or** a `shopbridge` package. Pick **one** import style and stick to it. The client CLI example is:

```text
python -m shopbridge --logical-date 2018-08-01
```

So a top-level `shopbridge` package is the path of least resistance. You can leave `src\` unused.

## 4.2 Empty files to create

Create empty `__init__.py` files and stub modules. `__main__.py` must parse:

- `--logical-date YYYY-MM-DD` (required)  
- `--full-refresh` (flag)  
- later: `--fail-on-quarantine-rate` (default off; 5% if set)

For now it can print the date and exit 0.

Test from the project root with venv on:

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
python -m shopbridge --logical-date 2018-08-01
```

**If `No module named shopbridge`:** you are not in the project root, or venv is off, or the folder is not named `shopbridge` with `__init__.py` inside.

**If Windows cannot create a `shopbridge` folder:** there is a file named `shopbridge` in the way. Rename the file.

## 4.3 Open decisions — pick now

Write these into `docs\requirements.md` §19. A simple set that satisfies the spec:

| Decision | Suggested choice |
|---|---|
| GMV | `price` only for item GMV; `freight_value` is a separate additive line measure |
| SCD2 current row | `valid_to = DATE '9999-12-31'` |
| Timezone | **No conversion** — naive timestamps, truncate to date as stored |
| Payments vs GMV | GMV = `SUM(price)` on items; amount collected = `SUM(payment_value)` on `fct_payments` |

## 4.4 Phase 4 exit check

- [ ] `python -m shopbridge --logical-date 2018-08-01` runs  
- [ ] §19 platform + GMV + SCD2 + timezone are not TBD  
- [ ] Layout exists; no business logic required yet  

---

# Phase 5 — CI fixtures (before full silver)

Create `tests\fixtures\` with **tiny** CSVs: **same column names** as Olist, **20–40 rows**.

Must include:

- One item with `price < 0` (Q-03)  
- One null `order_id` (Q-01)  
- One duplicate item key (Q-06)  
- One order with two payment rows (fan-out trap)  
- Dates around `2018-08-01` (client idempotency date)  
- Enough customers to test SCD2 later (or generate versions in code)

These fixtures are what GitHub Actions will run. Full `data\raw` is only for your demo.

**If you skip fixtures:** CI cannot run without downloading Olist. Do not skip.

**If column names do not match Olist:** quality tests will lie. Copy headers from the real CSVs.

**If `.gitignore` has `*.csv`:** fixtures would be ignored. Either put fixtures under `tests/fixtures/` and add `!tests/fixtures/*.csv` to `.gitignore`, or do not use a global `*.csv` ignore (your current ignore of `data/raw/*` is enough).

## 5.1 Phase 5 exit check

- [ ] Fixture CSVs committed (they are tiny; this is allowed)  
- [ ] You can explain which fixture row should quarantine  

---

# Phase 6 — Bronze (Milestone M2)

## Goal

Land all **nine** sources as bronze tables with:

- original columns (snake_case OK if documented)  
- `ingestion_ts`  
- `source_file_name`  
- `logical_date`  

**No business cleaning.**

## Option B — implement

- Read CSV from `data\raw\`  
- Write to DuckDB `data\warehouse\shopbridge.duckdb`, schema `shopbridge_dev`, tables `bronze_orders`, `bronze_order_items`, …  

Because Olist is a **static snapshot**, a valid v1 is:

- Each run restates bronze for that `logical_date` from the same files  
- For that date: delete where `logical_date = :ds` then insert, **or** replace that slice so a second run does not double rows  

Document: *“Source is a snapshot; each run restates bronze for that logical_date from the same files.”*

**If DuckDB file is locked:** close other Python processes, DBeaver, or any DuckDB extension in the editor.

**If encoding errors:** try `utf-8`, then `utf-8-sig`, then `latin-1`.

**If Windows paths break DuckDB:** use `pathlib.Path(...).as_posix()`.

**If row counts are 0:** wrong path; print the resolved path before read.

**If row counts are ~2× CSV:** you appended. Fix replace-by-`logical_date`.

Peek after a run (venv on):

```cmd
python -c "import duckdb; c=duckdb.connect(r'data/warehouse/shopbridge.duckdb'); print(c.execute(\"show tables\").fetchall())"
```

## Option A — implement

- Upload CSVs to a Volume or workspace files — **not Git**  
- Create Delta tables `shopbridge_dev.bronze_*` with the three metadata columns  
- Parameterize `logical_date`  

**If you cannot upload files on Free Edition:** switch the **whole** project to Option B and update §19. Do not burn weeks on quota.

**If serverless will not start:** wait and retry; if it fails two days, switch to B.

## Bronze exit check (both)

- [ ] Nine bronze tables  
- [ ] Metadata columns present  
- [ ] Row counts ≈ CSV lines minus header  
- [ ] Re-run same `logical_date` does not double bronze rows  
- [ ] Download script documented  

---

# Phase 7 — Silver + quarantine (Milestone M3)

## Goal

One silver table per entity you use (orders, items, customers, products, sellers, payments, reviews, translations; geo optional).

- Types (timestamps, decimals, ints)  
- Dedup on natural keys  
- Q-01–Q-06 → quarantine, **not** gold  
- W-01–W-03 → still load, emit metrics  
- Last source state wins (upsert)  
- 7-day lookback documented: incremental processes purchase dates in `[ds-7, ds]`

### Natural keys

| Entity | Key |
|---|---|
| orders | `order_id` |
| order_items | `order_id` + `order_item_id` |
| customers | `customer_id` |
| products | `product_id` |
| sellers | `seller_id` |
| payments | `order_id` + `payment_sequential` (confirm on your file) |
| reviews | `review_id` (document if not unique) |

### Build order

1. `quality.py` — flag Q/W rules; unit-test on fixtures first  
2. Items silver + `silver_quarantine_order_items`  
3. Orders silver + `silver_quarantine_orders`  
4. Other entities  
5. Q-06: keep one survivor (document the tiebreaker: e.g. last row / max `order_item_id`), extras to quarantine  

**If almost everything quarantines:** types failed (price still a string) or a rule is wrong. Fix types first.

**If silver is empty:** filter/join bug. Run the same functions on 20 fixture rows.

**If lookback feels fake on a snapshot:** still implement the filter. Document that the source does not actually change day to day. Full-refresh reads all silver.

**If `price` looks like `10.99` as string:** cast with a safe decimal; failed casts → quarantine, do not crash the date.

## Silver exit check

- [ ] Negative prices are **not** in silver items; they are in quarantine  
- [ ] Q-01–Q-06 exist  
- [ ] `docs\quality.md` started  
- [ ] Incremental path uses the lookback window  

---

# Phase 8 — Gold stars

Implement the tables in `docs\requirements.md` §8.1. Order:

1. `dim_date` — generate **2016-01-01 through 2018-12-31** (full calendar, not distinct fact dates)  
2. `dim_product` — English category via translation; missing → `'unknown'`; do not drop the product  
3. `dim_seller`  
4. `dim_customer` stub (Type 1 is OK **only if** Phase 9 follows immediately)  
5. `fct_order_items` — grain `order_id` + `order_item_id`  
6. `fct_orders` — no item price stored as if it were unique per order  
7. `fct_payments`  
8. `fct_reviews`  

Rebuild gold from **silver only**.

**Forbidden:** joining payments or reviews into `fct_order_items`.

**If `dim_date` has holes:** you used distinct fact dates. Generate a calendar.

**If orphans:** keep the item; put product category `unknown`.

**If `SUM(price)` looks like payment totals:** you joined payments. Undo that.

## Gold exit check

- [ ] `fct_order_items` unique on `order_id` + `order_item_id`  
- [ ] `SUM(price)` is stable  
- [ ] The eight business questions are *possible* (SQL comes in Phase 12)  

---

# Phase 9 — SCD2 customers (required)

Olist is a snapshot. You must **simulate ≥ 20 customers** with two versions **in gold generation**, not by editing bronze.

Example rule (document the date you pick):

- On `logical_date = 2018-06-01` (or another documented date)  
- For ≥ 20 `customer_id`s: close the old row (`valid_to` = that date, `is_current` = false)  
- Insert a new row with a changed `customer_state` (or city), `valid_from` = that date, `valid_to` = 9999-12-31, `is_current` = true  
- Half-open: new `valid_from` equals old `valid_to`  
- Facts: point-in-time join on order date **or** store `customer_sk` at load. Write which in `docs\model.md`

**If a date matches two versions:** intervals are not half-open. Join `d >= valid_from AND d < valid_to`.

**If every customer has two rows:** you applied the simulation to the whole table. Limit to ≥ 20 ids.

## SCD2 exit check

- [ ] ≥ 20 `customer_id`s have two rows  
- [ ] Exactly one `is_current = true` per `customer_id`  
- [ ] A query shows state before vs after the change date  

---

# Phase 10 — Wire the run, ops, idempotency

## 10.1 One command

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
.\.venv\Scripts\activate.bat
python -m shopbridge --logical-date 2018-08-01
python -m shopbridge --logical-date 2018-08-01 --full-refresh
```

Exit `0` on success / success_with_warnings. Non-zero on crash or fail-on-quarantine.

**Option A:** same parameters on a Job or notebook widgets. Document the click path in §19.

**Backfill:** a documented loop of daily dates is enough. Parallelism is optional.

```cmd
python -m shopbridge --logical-date 2018-08-01
python -m shopbridge --logical-date 2018-08-02
```

## 10.2 `ops_pipeline_run`

One row (or JSON) per run:

- `logical_date`  
- `started_at` / `ended_at` / duration  
- rows in / out for orders and items  
- quarantine counts  
- `success` / `success_with_warnings` / `failed`  

Prefer a DuckDB/Delta table. A JSON file under `data\warehouse\ops\` is acceptable if gitignored.

## 10.3 Idempotency (the client will do this)

1. Run `--logical-date 2018-08-01`  
2. Record `COUNT(*)` and `SUM(price)` on `fct_order_items`  
3. Run the same date again  
4. Numbers must match  

Automate against **fixtures** in `tests\test_idempotency.py`.

**If counts grow:** you append. Use replace/MERGE for that date or key.  
**If SUM changes but COUNT does not:** survivor rule is unstable. Add a deterministic tiebreaker.

## 10.4 Phase 10 exit check

- [ ] Two runs, same checksum  
- [ ] Ops row exists  
- [ ] §19 has “How to run one day” and “How to backfill”  

---

# Phase 11 — Tests and CI

## 11.1 Local tests

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
.\.venv\Scripts\activate.bat
pytest -q
```

Minimum:

- Q/W rules on fixtures  
- Unique keys on gold (fixture warehouse)  
- `fct_order_items.product_id` exists in `dim_product`  
- `order_status` in the documented set  
- Idempotency  
- GMV is **not** the result of a naive items×payments join  

**If `pytest` is not found:** venv off, or `pip install -r requirements.txt` again.  
**If imports fail:** run from the repo root. Optionally `pip install -e .` if you add `pyproject.toml`.  
**If tests hit `data\raw`:** wrong. Point tests at `tests\fixtures` only.

## 11.2 GitHub Actions

Create `.github\workflows\ci.yml`:

- Triggers: push to `main`, pull_request  
- Runner: `ubuntu-latest` (simpler than `windows-latest`)  
- Python 3.11  
- `pip install -r requirements.txt`  
- `pytest`  

CI must **not** download Olist.

**If Actions is red on paths:** you used Windows paths in Python. Use `pathlib`.  
**If you have no GitHub remote working:** local `pytest` is the documented one-command until you fix the remote. Client prefers green CI.

You already have `origin`. Push after tests pass:

```cmd
git add -A
git status
git commit -m "Add tests and CI"
git push -u origin main
```

**If push is rejected:** `git pull --rebase origin main` then push. Do not `--force` on `main` unless you know why.

**If you leaked `kaggle.json` or a Databricks token:** rotate the token; do not only delete the file.

## 11.3 Phase 11 exit check

- [ ] `pytest -q` green locally  
- [ ] CI green **or** README explains local-only tests  

---

# Phase 12 — Documentation and eight SQLs

Required files:

| File | What to write |
|---|---|
| `docs\model.md` | Grain sentences from §8.1, SCD2, GMV vs payments, fan-out warning, join path for each of the 8 questions |
| `docs\quality.md` | Q/W table, quarantine names, `order_status` set |
| `analysis\example_questions.sql` | **8 queries**, one-line comment each |
| Root `README.md` | Overview, architecture, stack, how to run, limitations, “Demo data: Olist public dataset.” |

Fill remaining §19 TBD: how to run tests, runtime (e.g. “full load < 30 min on my laptop”), limitations (“static dataset, simulated SCD2”).

**If you cannot write SQL for a business question:** a gold table is missing. Return to Phase 8. Do not make a wide denormalized table the source of truth.

## 12.1 Phase 12 exit check

- [ ] Eight SQLs run against gold  
- [ ] Model + quality docs exist  
- [ ] Root README is no longer a skeleton  

---

# Phase 13 — Full extract + self-review

1. Run a full load (`--full-refresh` or the snapshot restatement you documented).  
2. Run the eight SQLs.  
3. Run idempotency on `2018-08-01`.  
4. Walk `docs\requirements.md` §14 and §15 yourself.

**If full load is slow:** Olist should finish in minutes on DuckDB. If you did all gold in row-by-row pandas, rewrite gold in SQL.

**If Option A quota kills the job:** wait for reset **or** migrate to Option B and document the switch. Incomplete A is worse than complete B.

**If disk is full:** delete extra zips and old DuckDB copies. Keep one `data\warehouse\shopbridge.duckdb`.

## 13.1 Phase 13 exit check = client acceptance list

- [ ] Public or shared Git repo  
- [ ] README + §19 complete  
- [ ] `docs\model.md` + `docs\quality.md`  
- [ ] Bronze → silver → gold on full Olist  
- [ ] SCD2 demo  
- [ ] Quarantine Q-01–Q-06  
- [ ] Idempotent `2018-08-01`  
- [ ] Eight SQLs  
- [ ] Tests (+ CI if possible)  
- [ ] Ops run log  
- [ ] A stranger can follow README in under 60 minutes (excluding download)

That is Milestone **M4**. Streaming, RAG, and dashboards stay out until the client accepts.

---

# Option A extras (Databricks only)

1. Signup: https://login.databricks.com/?dbx_source=docs&intent=CE_SIGN_UP  
2. Use **serverless** only.  
3. Schema `shopbridge_dev` (default catalog + that schema is fine).  
4. Prefer managed Delta tables.  
5. Parameterize `logical_date`.  
6. Full names: `catalog.shopbridge_dev.fct_order_items`.  
7. GitHub CI tests **Python quality functions** on fixtures. Run SQL tests in the workspace for the demo.  
8. `.env` may hold `DATABRICKS_HOST` / `DATABRICKS_TOKEN`. Never commit `.env`. Copy from `.env.example`.

**If Free Edition has no Jobs:** a notebook with widgets `logical_date` and `full_refresh` is acceptable if README shows exact clicks. Python modules must still live in Git.

**If compute quota hits:** export DDLs, switch to Option B, update §19.

**If Unity Catalog will not let you create a catalog:** use the workspace default catalog and create schema `shopbridge_dev` only.

---

# Daily working rhythm

```cmd
cd /d D:\Projects\shopbridge-lakehouse-pipeline
.\.venv\Scripts\activate.bat
python -m shopbridge --logical-date 2018-08-01
pytest -q
git add <files you changed>
git commit -m "Add silver order dedup"
```

Always activate the venv first. Always run commands from the project root.

---

# Progress tracker

Tick as you finish exit checks.

| Phase | Milestone | Done? |
|---|---|---|
| 0 Machine setup | — | |
| 1 Repo hygiene | M1 | |
| 2 Data verify + download script | — | |
| 3 Source study | — | |
| 4 Skeleton + CLI stub | — | |
| 5 Fixtures | — | |
| 6 Bronze | M2 | |
| 7 Silver + quarantine | M3 | |
| 8 Gold stars | M4 start | |
| 9 SCD2 | M4 | |
| 10 Ops + idempotency | M4 | |
| 11 Tests + CI | M4 | |
| 12 Docs + 8 SQLs | M4 | |
| 13 Full run + §14/§15 | M4 accept | |

---

# Quick failure map

| Symptom | What to try |
|---|---|
| Cursor opened the wrong folder | Open `D:\Projects\shopbridge-lakehouse-pipeline` |
| `activate.bat` will not run | Use cmd, not PowerShell; or `Activate.ps1` after `RemoteSigned` |
| Wrong Python | Delete `.venv`, `py -3.11 -m venv .venv` |
| `pip` SSL error | `--trusted-host` or phone hotspot; drop VPN |
| Kaggle 401 | New token in `%USERPROFILE%\.kaggle\kaggle.json` |
| CSVs appear in `git status` | Fix `.gitignore`, `git rm --cached` |
| `No module named shopbridge` | `cd /d D:\Projects\shopbridge-lakehouse-pipeline`, venv on |
| DuckDB “file is locked” | Close other connections; do not delete `-wal` while a process is open |
| Encoding error on CSV | `utf-8` → `utf-8-sig` → `latin-1` |
| Duplicate gold rows on rerun | REPLACE/MERGE; no append |
| GMV exploded | You joined payments or reviews onto items |
| SCD2 double match | Half-open dates |
| pytest cannot import | Repo root + venv |
| Databricks wants a card | Option B immediately |
| Spark on Windows | Do not install; stay on DuckDB |
| `setup.sh` errors | Ignore it; this is Windows |
| Disk full | Delete zip copies; one DuckDB file |
| Push rejected | `git pull --rebase origin main` then push; no force on main |
| Fixture CSVs ignored by Git | Do not use global `*.csv` without `!tests/fixtures/*.csv` |

---

# What not to do

- Do not start a second warehouse (Snowflake + Databricks).  
- Do not commit `data\raw` CSVs, `.env`, or `kaggle.json`.  
- Do not build Tableau/Power BI as the deliverable.  
- Do not install Spark, Java, Docker, or Kubernetes for v1.  
- Do not run `setup.sh` on Windows.  
- Do not skip fixtures and hope CI downloads Olist.  
- Do not implement in `Downloads\Job Application\olist-lakehouse` — that folder is only a copy of docs.

---

# Start here tomorrow morning

1. Open `D:\Projects\shopbridge-lakehouse-pipeline` in Cursor.  
2. Phase 0 checks (`git --version`, `py -3.11 --version`).  
3. Write Option A or B in `docs\requirements.md` §19.  
4. Create `.venv` and `requirements.txt` (Phase 1).  
5. Confirm nine CSVs and write `scripts\download_data.py` (Phase 2).  
6. Study grains (Phase 3).  
7. Stub `python -m shopbridge --logical-date 2018-08-01` (Phase 4).  

Stop at the first red exit check. Fix it before bronze.

---

*Playbook for `D:\Projects\shopbridge-lakehouse-pipeline`. Contract remains `docs\requirements.md`.*
