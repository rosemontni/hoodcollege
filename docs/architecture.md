# Coding Architecture

## Architecture Goal

The implementation should be easy to:

- maintain
- test
- modify
- expand
- scale
- replace module by module

The safest fit for this project is a **layered ports-and-adapters architecture** with thin workflow orchestration on top.

## Design Principles

### 1. Keep the domain small and stable

Core concepts like article, person mention, source item, and connection should live in plain Python models with minimal dependencies.

### 2. Put change at the edges

HTTP fetching, HTML parsing, LLM extraction, SQLite storage, markdown writing, and GitHub Actions behavior should be isolated behind interfaces.

### 3. Make every workflow rerunnable

Daily and weekly runs should be deterministic from stored inputs wherever possible so reprocessing is cheap and safe.

### 4. Prefer composition over giant modules

Each pipeline stage should be a small service with one responsibility and explicit inputs and outputs.

### 5. Preserve traceability

Every derived record should be traceable back to article evidence and the processing run that created it.

## Recommended Layering

### Domain layer

Contains stable business concepts and rules:

- article
- source item
- person candidate
- person mention
- canonical person
- connection
- evidence snippet
- confidence assessment

This layer should not import HTTP clients, database code, or OpenAI clients.

### Application layer

Contains use cases and orchestration services:

- fetch new source items
- ingest article content
- disambiguate Hood relevance
- extract people
- promote canonical people
- derive connections
- write daily stories
- write weekly reports
- reprocess stale items

This layer coordinates work through interfaces but does not care whether the backing implementation is SQLite, Postgres, requests, or OpenAI.

### Ports layer

Defines interfaces for replaceable dependencies:

- `SourceRegistry`
- `SourceReader`
- `ArticleFetcher`
- `ArticleExtractor`
- `Disambiguator`
- `PeopleExtractor`
- `PersonRepository`
- `ArticleRepository`
- `ConnectionRepository`
- `DiscoveryWriter`
- `Clock`
- `RunJournal`

These are the main seams for testing and replacement.

### Infrastructure layer

Contains concrete adapters:

- RSS or page feed readers
- HTTP fetch client
- HTML cleaner
- OpenAI-backed people extractor
- heuristic fallback extractor
- SQLite repositories
- markdown file writers
- local filesystem run journal

### Interface layer

Contains user-facing entry points:

- CLI commands
- scheduled workflow entry scripts
- future API or dashboard endpoints if needed

## Suggested Repository Layout

```text
src/
  hood_pipeline/
    __init__.py
    cli.py
    config.py
    domain/
      models.py
      enums.py
      rules.py
    application/
      daily_run.py
      weekly_run.py
      reprocess.py
      ingest_article.py
      extract_people.py
      build_connections.py
      write_discovery.py
    ports/
      sources.py
      fetching.py
      extraction.py
      repositories.py
      writing.py
      runtime.py
    infrastructure/
      sources/
        hood_news.py
        hood_athletics.py
      fetching/
        http_fetcher.py
        readability_extract.py
      extraction/
        openai_people_extractor.py
        heuristic_people_extractor.py
        hood_disambiguator.py
      persistence/
        sqlite_db.py
        article_repo.py
        person_repo.py
        connection_repo.py
      writing/
        markdown_discovery_writer.py
        markdown_connection_writer.py
      runtime/
        local_clock.py
        local_run_journal.py
tests/
  unit/
  integration/
  fixtures/
sources/
data/
docs/
research/
```

## Workflow Shape

### Daily run

Suggested pipeline:

1. read source definitions
2. fetch source items
3. deduplicate against known URLs
4. fetch article content
5. normalize and archive article text
6. disambiguate Hood relevance
7. extract people and article-scoped metadata
8. persist mentions and promoted people
9. write daily markdown story
10. mark run results in journal

Each step should return typed results so it can be tested independently.

### Weekly run

Suggested pipeline:

1. load the last 7 days of accepted evidence
2. derive candidate connections
3. score and filter weak links
4. write markdown weekly report
5. persist connection snapshots

## Module Replacement Strategy

The architecture should support replacing each of these without disturbing the rest of the system:

### Replace the people extractor

Example:

- start with heuristic extraction
- switch to OpenAI extraction later
- run both during evaluation

This works if the application layer depends only on a `PeopleExtractor` port.

### Replace storage

Example:

- start with SQLite
- move to Postgres later if volume grows

This works if repositories implement the same repository ports.

### Replace source readers

Example:

- start with `hood.edu` news and `hoodathletics.com`
- add selected Frederick publishers later

This works if each source type is a small adapter registered in the source registry.

### Replace report writers

Example:

- start with markdown files
- later also publish JSON, HTML, or a dashboard feed

This works if report generation returns structured report data before rendering.

## Testing Strategy

### Unit tests

Fast tests for:

- disambiguation rules
- confidence scoring
- role classification
- connection scoring
- markdown rendering

These should run without network or database I/O.

### Integration tests

Focused tests for:

- source reader parsing
- article fetch and extract flow
- SQLite repository behavior
- end-to-end daily run on fixture articles

These should use local fixtures and temporary databases.

### Fixture strategy

Store representative fixture pages for:

- clean Hood news articles
- Hood athletics recaps
- ambiguous `Hood` mentions
- person-rich partnership pages
- person-light articles

This is critical for regression testing when extraction logic changes.

## Data And Processing Boundaries

### Raw data

Keep raw or normalized article inputs available for reprocessing.

### Derived data

Store article-scoped person mentions separately from canonical people.

### Published outputs

Treat markdown stories and weekly reports as renderable outputs, not as the source of truth.

The database and archived article evidence should remain the source of truth.

## Configuration Strategy

Split configuration into:

- source configuration
- runtime configuration
- model configuration
- output paths
- threshold tuning

Avoid scattering settings across modules. A single config loader should validate values at startup.

## Scaling Strategy

The first implementation can stay simple, but these choices keep scaling options open:

- use idempotent workflow steps
- separate fetch, extract, and publish phases
- persist status per article
- track processing version per extractor
- support batch reprocessing by date range or extractor version

If throughput grows later, fetch and extraction can be parallelized without rewriting domain logic.

## Change Management

When behavior changes materially, add a small architecture decision record or update this file.

Good candidates for explicit decisions:

- adding new source families
- changing canonical person identity rules
- changing confidence thresholds
- introducing a second storage backend
- changing the LLM provider or extraction strategy

## Recommendation For The First Coding Pass

Build in this order:

1. domain models and repository ports
2. SQLite repositories
3. source readers for `hood.edu` and `hoodathletics.com`
4. article fetch and disambiguation flow
5. article-scoped people extraction
6. markdown discovery writer
7. weekly connection builder

That order gives us a working vertical slice early while keeping the highest-change modules isolated.
