# Hood College Signal Atlas

Hood College Signal Atlas is a Python pipeline for **Hood College in Frederick, Maryland**. It collects official source coverage, filters for Hood-specific relevance, extracts plausible person mentions, stores article-level evidence in SQLite, and writes markdown discovery outputs.

The project is designed around four repeatable jobs:

1. collect Hood College coverage from trusted sources
2. extract people and preserve evidence from each article
3. write a daily discovery summary in markdown
4. derive weekly co-mention connections from stored evidence

The current codebase already includes:

- a runnable CLI
- source readers for paginated `hood.edu/news`, paginated `hood.edu/discover/stories`, RSS/Atom feeds, selected Frederick-area media feeds, and Reddit search feeds
- SQLite storage
- conservative Hood-specific disambiguation
- a heuristic people extractor designed for easy replacement later
- markdown daily and weekly output writers
- unit tests for key first-slice behavior

## Why This Shape

This project is modeled after lessons learned in the `network` reference repo:

- start with clean official sources before adding broader media
- prefer traceable evidence over aggressive extraction
- store lower-confidence findings only when they remain inspectable
- delay connection analysis until person quality is good enough
- make reprocessing part of the design from the beginning

## Scope Guardrail

This repository is only about **Hood College at 401 Rosemont Ave., Frederick, MD 21701**, including its official academic, student-life, and athletics presence.

It must explicitly avoid false matches from similarly named institutions, places, organizations, or people.

## Outputs

- article records with normalized body text and relevance decisions
- best-effort inferred story dates, along with the source of each date inference
- article-scoped person mention records
- official faculty/staff directory records from `hood.edu/academics/faculty`, retained with active status and last-seen dates
- daily markdown discovery stories
- weekly markdown cumulative connection reports
- monthly markdown reports for the prior calendar month, including a newspaper-style essay about what happened at Hood
- cumulative summary table, discovery-growth graph, top-25 connection network graph, and a draggable HTML network view
- a local SQLite database that preserves article-level evidence

## Quick Start

```powershell
python -m pip install -r requirements.txt -e .
python -m hood_pipeline init-db
python -m hood_pipeline daily-run
python -m hood_pipeline weekly-run
python -m hood_pipeline monthly-run --date 2026-05-01
python -m hood_pipeline import-faculty-staff
python -m hood_pipeline build-pages
```

The default source configuration lives in `sources/hood_sources.json`.

## CLI

```powershell
python -m hood_pipeline init-db
python -m hood_pipeline daily-run --date 2026-03-20
python -m hood_pipeline weekly-run --date 2026-03-20
python -m hood_pipeline monthly-run --date 2026-05-01
python -m hood_pipeline import-faculty-staff --date 2026-04-29
python -m hood_pipeline build-pages --output-dir _site
```

Supported commands:

- `init-db`: create the SQLite schema
- `daily-run`: fetch sources, ingest articles, extract people, and write the daily discovery
- `weekly-run`: build a cumulative co-mention network snapshot and write the weekly report
- `monthly-run`: publish a newspaper-style monthly story for the month that just ended, keyed to article story dates instead of fetch dates
- `import-faculty-staff`: import the official paginated Hood faculty directory into SQLite, mark current entries active, retain prior entries, and write a markdown directory report
- `build-pages`: build a static GitHub Pages site from the generated summary artifacts

The daily run also refreshes:

- `data/summary/discovery-summary.md`
- `data/summary/discovery-growth.svg`
- `data/summary/connection-network.svg`
- `data/summary/connection-network.html`

On the first day of each month, `daily-run` also publishes:

- `data/monthly/YYYY-MM.md`

The Pages build writes a publishable static site to `_site/` by default, wrapping the interactive network, discovery graph, cumulative discovery table, and latest monthly story into one browser-friendly landing page.

## CI/CD

GitHub Actions workflows now live in `.github/workflows/`:

- `ci.yml`: runs the unit test suite on pushes to `main` and on pull requests
- `daily-pipeline.yml`: runs the daily Hood pipeline on a schedule and commits generated `data/` outputs back to `main`
- `weekly-pipeline.yml`: runs the weekly connections report on a schedule and commits generated `data/` outputs back to `main`
- `pages.yml`: builds and deploys the GitHub Pages site from the current summary artifacts on `main`

The Pages workflow runs after normal pushes to relevant code, docs, and generated summary paths. It also runs after successful scheduled daily or weekly pipeline runs, so GitHub Pages is refreshed from the latest committed `data/summary/` and `data/monthly/` artifacts even when the update was produced by GitHub Actions.

Current schedules:

- daily pipeline: `13:05 UTC` every day
- weekly connections: `13:35 UTC` every Sunday

In `America/New_York`, those map to:

- daily pipeline: `9:05 AM EDT` or `8:05 AM EST`
- weekly connections: `9:35 AM EDT` or `8:35 AM EST`

## Runtime Paths

By default the pipeline writes to:

- `data/hood_people.db`
- `data/discoveries/YYYY-MM-DD.md`
- `data/connections/YYYY-MM-DD.md`
- `data/directory/faculty-staff-directory.md`
- `data/monthly/YYYY-MM.md`

These can be overridden with environment variables:

- `HOOD_PIPELINE_DATA_DIR`
- `HOOD_PIPELINE_DATABASE_PATH`
- `HOOD_PIPELINE_DISCOVERIES_DIR`
- `HOOD_PIPELINE_CONNECTIONS_DIR`
- `HOOD_PIPELINE_DIRECTORY_DIR`
- `HOOD_PIPELINE_MONTHLY_REPORTS_DIR`
- `HOOD_PIPELINE_SUMMARY_DIR`
- `HOOD_PIPELINE_SOURCES_PATH`
- `HOOD_PIPELINE_USER_AGENT`
- `HOOD_PIPELINE_REQUEST_TIMEOUT`

## Repository Layout

- `src/hood_pipeline/`: application, domain, ports, and infrastructure code
- `tests/`: unit tests for the first implementation slice
- `sources/`: source configuration
- `research/`: source notes and collection research
- `docs/`: planning and architecture documents

## Documentation

- [docs/getting-started.md](docs/getting-started.md)
- [docs/operations.md](docs/operations.md)
- [docs/project-plan.md](docs/project-plan.md)
- [docs/source-strategy.md](docs/source-strategy.md)
- [docs/data-model.md](docs/data-model.md)
- [docs/architecture.md](docs/architecture.md)

## Repository Metadata

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [CODEOWNERS](CODEOWNERS)

## Current Status

Planning baseline complete.
First coding slice implemented and runnable.

Current limitations:

- extraction is still heuristic and intentionally conservative
- person canonicalization is still basic
- weekly connections are currently co-mention based, not richer relationship inference
- GitHub Actions automation is implemented, but the scheduled data outputs still depend on the current heuristic extractor quality
- the GitHub Pages site is only as fresh as the latest committed `data/summary/` artifacts
