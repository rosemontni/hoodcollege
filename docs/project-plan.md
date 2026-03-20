# Hood College Project Plan

## Mission

Build a daily intelligence workflow for **Hood College in Frederick, Maryland** that collects relevant coverage, extracts people with context, writes a short story-like daily summary, and produces a weekly analysis of connections across the observed people.

## Primary Requirements

1. Perform daily intelligence gathering about Hood College in Frederick, Maryland.
2. Prevent confusion with similarly named colleges or unrelated organizations.
3. Record every encountered person with role-specific metadata.
4. Produce a short markdown story each day from newly discovered people and article activity.
5. Produce a weekly connection report from the growing database.

## Lessons Applied From The Reference Project

### 1. Bootstrap with official sources first

Initial collection should focus on official Hood-owned or Hood-operated sources before broader local media is added.

### 2. Store evidence, not just names

Each person record should be tied back to article context, source URL, publication date, quoted text when available, and confidence notes.

### 3. Prefer cautious recall over empty output

The first version should allow clearly plausible person matches, but mark uncertainty and keep article-level provenance attached.

### 4. Delay graph-heavy claims

Weekly relationship reporting should be descriptive and evidence-based until extraction quality is mature enough for stronger network assertions.

### 5. Reprocess often

If extraction rules or source selection changes, recent articles should be reprocessed automatically.

## Execution Cadence

### Daily workflow

1. Fetch newly published or recently updated source items.
2. Normalize and archive article content.
3. Reject likely non-Hood or ambiguous items.
4. Extract people and classify each person mention.
5. Store article-level mention records plus promoted canonical people records.
6. Write a markdown discovery story for that day.

### Weekly workflow

1. Review the prior 7 days of article-person evidence.
2. Build connections from co-mentions, shared departments, shared teams, shared events, and shared programs.
3. Publish a weekly connection brief with evidence links and confidence notes.

## Phase Plan

### Phase 0: planning baseline

- finalize source strategy
- define disambiguation rules
- define schema and output formats
- set repository structure

### Phase 1: ingestion and storage

- build source configuration
- fetch article pages
- store normalized article records
- create the local SQLite database

### Phase 2: person extraction

- extract candidate people from article text
- classify role type
- attach evidence and confidence
- promote only plausible person records

### Phase 3: discovery writing

- generate daily markdown stories
- group mentions by theme, event, or community context
- keep the story grounded in traceable source evidence

### Phase 4: connection discovery

- derive weekly co-mention and shared-context links
- score connections by evidence density
- publish a concise weekly connection report

### Phase 5: broader coverage

- add carefully chosen Frederick-area publisher sources
- preserve strict Hood-specific disambiguation
- monitor noise before expanding further

## Deliverables For The Coding Phase

- CLI command for daily run
- CLI command for weekly connections run
- source config file
- SQLite schema and migrations
- markdown output writers
- scheduled GitHub Actions workflow

## Success Criteria

- every stored person can be traced back to one or more source articles
- ambiguous Hood references are filtered or flagged before storage
- daily stories remain readable by a human and link back to evidence
- weekly connection reports avoid unsupported claims
- reprocessing can improve old outputs without manual cleanup
