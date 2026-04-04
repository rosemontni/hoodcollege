# Getting Started

## Purpose

This guide explains how to install and run the first implementation slice of Hood College Signal Atlas.

## Prerequisites

- Python 3.11 or newer
- network access to the configured sources
- write access to the repository working tree

## Install

From the repository root:

```powershell
python -m pip install -r requirements.txt -e .
```

This installs:

- runtime dependencies from `requirements.txt`
- the local package in editable mode so `python -m hood_pipeline` works during development

## Initialize The Database

```powershell
python -m hood_pipeline init-db
```

Default database path:

- `data/hood_people.db`

## Run The Daily Pipeline

```powershell
python -m hood_pipeline daily-run
```

Or for a specific date:

```powershell
python -m hood_pipeline daily-run --date 2026-03-20
```

The daily run:

1. loads source definitions from `sources/hood_sources.json`
2. fetches source items
3. fetches and cleans article pages
4. applies Hood-specific disambiguation
5. extracts person mentions
6. stores article and mention records in SQLite
7. writes a daily markdown story
8. updates the cumulative discovery summary table and graph

## Run The Weekly Report

```powershell
python -m hood_pipeline weekly-run
```

Or for a specific week-ending date:

```powershell
python -m hood_pipeline weekly-run --date 2026-03-20
```

The weekly run currently derives co-mention connections from the last 7 days of stored mentions.

## Run Tests

```powershell
python -m unittest discover -s tests
```

## GitHub Actions

The repository now includes these workflows:

- `.github/workflows/ci.yml`
- `.github/workflows/daily-pipeline.yml`
- `.github/workflows/weekly-pipeline.yml`

You can run the scheduled workflows manually from the GitHub Actions tab using `workflow_dispatch`.

## Configuration

The current source registry is stored in:

- `sources/hood_sources.json`

Supported environment variables:

- `HOOD_PIPELINE_DATA_DIR`
- `HOOD_PIPELINE_DATABASE_PATH`
- `HOOD_PIPELINE_DISCOVERIES_DIR`
- `HOOD_PIPELINE_CONNECTIONS_DIR`
- `HOOD_PIPELINE_SUMMARY_DIR`
- `HOOD_PIPELINE_SOURCES_PATH`
- `HOOD_PIPELINE_USER_AGENT`
- `HOOD_PIPELINE_REQUEST_TIMEOUT`

## Current Behavior Notes

- `hood.edu/news` is read from the HTML news index and follows pagination
- `hood.edu/discover/stories` is read from the official stories index and follows pagination
- Hood athletics uses an RSS feed reader
- Reddit uses public Atom search feeds, filtered down to actual post URLs
- Frederick-area media can be added through direct RSS/search feeds, with optional title-summary keyword gates before article fetch
- article extraction is intentionally conservative and still heuristic
- the database is the source of truth; markdown files are rendered outputs
