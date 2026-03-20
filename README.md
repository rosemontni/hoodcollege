# Hood College Signal Atlas

Hood College Signal Atlas is a Python pipeline for **Hood College in Frederick, Maryland** that fetches official source coverage, extracts plausible people mentions, stores article-level evidence, and writes markdown discovery outputs.

The project goal is to:

1. collect new Hood College coverage each day from carefully chosen sources
2. extract the people mentioned in that coverage
3. store role-aware person records with article evidence and traceable provenance
4. publish a short markdown discovery story each day
5. publish a weekly relationship report describing meaningful connections between the people observed

The first coding slice is now in place:

- a runnable CLI
- source readers for `hood.edu/news` and the Hood athletics RSS feed
- SQLite storage
- conservative Hood-specific disambiguation
- a heuristic people extractor designed for easy replacement later
- markdown daily and weekly output writers

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

- daily article intake records
- daily person mention records
- daily markdown discovery stories
- weekly connection summaries
- a local database that preserves article-level evidence

## Quick Start

```powershell
python -m pip install -r requirements.txt -e .
python -m hood_pipeline init-db
python -m hood_pipeline daily-run
python -m hood_pipeline weekly-run
```

The default source configuration lives in `sources/hood_sources.json`.

## Repository Layout

- `src/hood_pipeline/`: application, domain, ports, and infrastructure code
- `tests/`: unit tests for the first implementation slice
- `sources/`: source configuration
- `research/`: source notes and collection research
- `docs/`: planning and architecture documents

## Planning Docs

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
