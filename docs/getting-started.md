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
8. updates the cumulative discovery summary table, discovery graph, top-25 connection network graph, and draggable connection-network HTML page

## Run The Weekly Report

```powershell
python -m hood_pipeline weekly-run
```

Or for a specific week-ending date:

```powershell
python -m hood_pipeline weekly-run --date 2026-03-20
```

The weekly run currently writes a cumulative co-mention network snapshot using all stored mentions observed up to the run date.

## Build The GitHub Pages Site

```powershell
python -m hood_pipeline build-pages --output-dir _site
```

This command packages the generated summary artifacts into a static site that GitHub Pages can serve directly, including:

1. an `index.html` landing page
2. the draggable `connection-network.html` page
3. the static SVG graphs
4. the discovery summary markdown snapshot

## Run Tests

```powershell
python -m unittest discover -s tests
```

## GitHub Actions

The repository now includes these workflows:

- `.github/workflows/ci.yml`
- `.github/workflows/daily-pipeline.yml`
- `.github/workflows/weekly-pipeline.yml`
- `.github/workflows/pages.yml`

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
