# Operations Guide

## Pipeline Overview

The current implementation has two primary workflows.

### Daily workflow

`daily-run` performs:

1. source loading
2. source item collection
3. article fetch and cleanup
4. Hood relevance filtering
5. person mention extraction
6. SQLite persistence
7. markdown discovery writing

### Weekly workflow

`weekly-run` performs:

1. loading article-scoped mentions from the prior 7 days
2. building pairwise co-mention connections
3. storing weekly connection rows
4. writing a markdown weekly report

## Source Registry

The source configuration file is:

- `sources/hood_sources.json`

Current source adapters:

- `hood_site_listing`: parse official Hood College listing pages such as `hood.edu/news` and `hood.edu/discover/stories`, including pagination
- `rss` and `feed`: parse RSS, Atom, and search-result feeds such as Hood athletics, Reddit, Frederick News-Post search, and selected local media feeds

Current active source registry includes:

- official Hood College news and stories pages
- Hood athletics RSS
- Frederick News-Post HTML search results for `hood college`
- WFMD, WFRE, and Key 103 / WAFY main RSS feeds, gated by Hood-specific prefetch keywords before article fetch
- Reddit search Atom feeds, filtered to comment-thread URLs

The architecture is designed so new source readers can be added without changing the workflow layer.

## Output Paths

Default outputs:

- database: `data/hood_people.db`
- daily discovery: `data/discoveries/YYYY-MM-DD.md`
- weekly report: `data/connections/YYYY-MM-DD.md`
- cumulative summary table: `data/summary/discovery-summary.md`
- cumulative discovery graph: `data/summary/discovery-growth.svg`

Generated runtime data is intentionally ignored by Git.

## Database Tables

Current tables:

- `articles`
- `people`
- `article_people`
- `weekly_connections`

The implementation is intentionally simple for the first slice. See [data-model.md](data-model.md) for the fuller planned model.

## Current Quality Strategy

The current quality approach favors traceable plausibility over aggressive recall:

- prefer official sources
- keep Hood disambiguation strict
- preserve article-scoped mention context
- avoid strong connection claims beyond co-mentions
- keep cumulative summary counts based on canonical `people.first_seen`

## GitHub Actions

The repository now includes:

- `ci.yml` for push and pull-request validation
- `daily-pipeline.yml` for scheduled daily collection
- `weekly-pipeline.yml` for scheduled weekly connection reporting

Current schedule details:

- daily run: 13:05 UTC every day
- weekly connections run: 13:35 UTC every Sunday

The scheduled workflows install dependencies, run the CLI, and commit generated `data/` outputs back to `main`.

## Known Limitations

- person extraction is heuristic and still produces some false positives
- person role assignment is best-effort rather than canonical
- weekly connections are shallow and based on co-mention counts
- reprocessing versioning is not implemented yet

## Recommended Development Order

The next implementation priorities should be:

1. improve person-role attribution and canonicalization
2. reduce remaining extractor false positives
3. add richer article metadata and source timestamps
4. improve weekly connection scoring
5. add scheduled automation through GitHub Actions

## Debugging Tips

If a run looks noisy:

- inspect the daily markdown file in `data/discoveries`
- inspect recent rows in `article_people`
- review the article cleaning logic in `src/hood_pipeline/infrastructure/fetching/http_fetcher.py`
- review the extraction filters in `src/hood_pipeline/infrastructure/extraction/heuristic_people_extractor.py`

If a valid article is missing:

- confirm the source appears in `sources/hood_sources.json`
- check whether the disambiguator rejected it
- review the source reader adapter for that site
