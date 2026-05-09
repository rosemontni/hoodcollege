# Operations Guide

## Pipeline Overview

The current implementation has four primary workflows plus a Pages publishing workflow.

### Daily workflow

`daily-run` performs:

1. source loading
2. source item collection
3. article fetch and cleanup
4. Hood relevance filtering
5. person mention extraction
6. SQLite persistence
7. markdown discovery writing
8. first-of-month prior-month report publishing

### Weekly workflow

`weekly-run` performs:

1. loading article-scoped mentions observed up to the run date
2. building pairwise cumulative co-mention connections
3. storing a cumulative connection snapshot
4. writing a markdown weekly network report

### Monthly workflow

`monthly-run` performs:

1. selecting the month that ended immediately before the supplied run date
2. loading relevant articles by inferred story date, not by fetch date
3. aggregating mentions across that monthly article set
4. writing a markdown monthly report with a newspaper-style essay to `data/monthly`

### Faculty/staff directory workflow

`import-faculty-staff` performs:

1. fetching the official paginated Hood faculty page at `https://www.hood.edu/academics/faculty`
2. parsing faculty directory cards, profile URLs, faculty types, titles, phone numbers, and emails
3. marking previously imported directory entries inactive before upserting entries seen in the current run
4. preserving historical rows even after someone no longer appears in the live directory
5. writing a markdown directory report to `data/directory/faculty-staff-directory.md`

### Pages workflow

`build-pages` performs:

1. validating the expected `data/summary/` artifacts exist
2. copying summary and monthly-report artifacts into a static-site output directory
3. generating an `index.html` landing page with the interactive graph, discovery graph, summary table, and latest monthly story
4. writing `.nojekyll` and `404.html` support files for GitHub Pages hosting

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
- faculty/staff directory report: `data/directory/faculty-staff-directory.md`
- monthly report: `data/monthly/YYYY-MM.md`
- cumulative summary table: `data/summary/discovery-summary.md`
- cumulative discovery graph: `data/summary/discovery-growth.svg`
- daily connection network graph: `data/summary/connection-network.svg`
- daily interactive connection network page: `data/summary/connection-network.html`

Generated runtime data is intentionally ignored by Git.
GitHub Actions force-adds the generated `data/` outputs when it commits scheduled pipeline updates back to `main`, and the Pages workflow reads from those committed summary artifacts.

## Database Tables

Current tables:

- `articles`
- `people`
- `article_people`
- `weekly_connections`
- `faculty_staff_directory`

The `faculty_staff_directory` table stores each person by profile URL, preserving the first import date, updating `last_seen_in_directory` whenever the live directory still lists the person, and setting `active` to false when a later non-empty import no longer includes that profile.

The implementation is intentionally simple for the first slice. See [data-model.md](data-model.md) for the fuller planned model.

## Current Quality Strategy

The current quality approach favors traceable plausibility over aggressive recall:

- prefer official sources
- keep Hood disambiguation strict
- infer article story dates from page-level structured signals before falling back to weaker clues
- preserve article-scoped mention context
- avoid strong connection claims beyond co-mentions
- keep cumulative summary counts based on canonical `people.first_seen`

## GitHub Actions

The repository now includes:

- `ci.yml` for push and pull-request validation
- `daily-pipeline.yml` for scheduled daily collection
- `weekly-pipeline.yml` for scheduled weekly connection reporting
- `pages.yml` for building and deploying the GitHub Pages site

Current schedule details:

- daily run: 13:05 UTC every day
- weekly connections run: 13:35 UTC every Sunday

The scheduled workflows install dependencies, run the CLI, and commit generated `data/` outputs back to `main`.
The first calendar-day run each month also publishes the previous month’s report because `daily-run` now triggers that step automatically on day 1.
The Pages workflow builds `_site/` from `data/summary/` and `data/monthly/` and deploys that artifact to the repository's GitHub Pages environment. It deploys after direct pushes to relevant paths and after successful daily or weekly pipeline completions, which keeps the site fresh even when generated data was committed by GitHub Actions.

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
6. refine the GitHub Pages site once the extraction quality stabilizes

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
