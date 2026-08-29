#!/bin/bash
# setup.sh
# Scaffolds a standard data engineering project folder structure.
# Reusable across projects: ShopBridge, streaming, AI/RAG, etc.

set -e  # stop the script if any command fails

echo "Creating project folder structure..."

# Source code (organized by pipeline stage)
mkdir -p src/extract src/transform src/load
touch src/__init__.py
touch src/extract/__init__.py
touch src/transform/__init__.py
touch src/load/__init__.py

# Tests
mkdir -p tests/fixtures
touch tests/__init__.py

# Documentation
mkdir -p docs
touch docs/model.md
touch docs/quality.md

# Analysis / example queries
mkdir -p analysis
touch analysis/example_questions.sql

# Data folders (never commit real data — see .gitignore below)
mkdir -p data/raw data/bronze data/silver data/gold

# Root-level files
touch requirements.txt

# .env.example — lists required env vars WITHOUT real values
cat > .env.example << 'EOF'
# Copy this file to .env and fill in real values.
# Never commit the actual .env file.

DATABRICKS_HOST=
DATABRICKS_TOKEN=
WAREHOUSE_NAME=
EOF

# .gitignore — protects secrets and raw data from being committed
cat > .gitignore << 'EOF'
# Environment / secrets
.env

# Data (never commit real data files)
data/raw/*
data/bronze/*
data/silver/*
data/gold/*
!data/raw/.gitkeep
!data/bronze/.gitkeep
!data/silver/.gitkeep
!data/gold/.gitkeep

# Python
__pycache__/
*.pyc
.venv/
venv/

# OS/editor files
.DS_Store
.vscode/
EOF

# Keep empty data folders tracked in Git (Git ignores empty folders by default)
touch data/raw/.gitkeep data/bronze/.gitkeep data/silver/.gitkeep data/gold/.gitkeep

# README skeleton (you'll expand this properly later)
cat > README.md << 'EOF'
# Project Name

## Overview
_What this project does and why._

## Architecture
_Diagram goes here (Mermaid.js or Excalidraw)._

## Tech Stack
_List tools used and why._

## How to Run
_Setup and run instructions._

## Known Limitations
_What you'd improve with more time._
EOF

echo "Done. Folder structure created:"
find . -maxdepth 2 -not -path './.git*'
