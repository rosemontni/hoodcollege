# Planned Data Model And Outputs

## Core Storage Model

The planned implementation should use SQLite with article-level evidence preserved.

### `articles`

Stores:

- source identifier
- canonical URL
- title
- publication timestamp
- fetch timestamp
- normalized body text
- content hash
- extraction status
- disambiguation status

### `people`

Stores canonical person records:

- canonical name
- person key
- primary role category
- primary organization
- department or office
- academic program or major
- class year
- athletics team
- hometown
- notes
- first seen date
- last seen date

### `article_people`

Stores article-scoped people evidence:

- article id
- person id
- displayed name
- role category
- role text
- department
- office
- major
- class year
- athletics team
- hometown
- quote or nearby evidence text
- confidence
- inclusion note

### `connections`

Stores derived weekly links:

- left person id
- right person id
- connection type
- shared context
- supporting article count
- confidence
- week start date

## Output Files

### Daily story

Planned path:

- `data/discoveries/YYYY-MM-DD.md`

Suggested structure:

1. title
2. short narrative story
3. source list
4. people observed

### Weekly connections report

Planned path:

- `data/connections/YYYY-MM-DD.md`

Suggested structure:

1. week label
2. strongest observed connections
3. notable clusters
4. evidence notes

## Record Quality Rules

- every promoted person record must have at least one source article
- every weekly connection must cite article support
- ambiguous matches should remain article-scoped until confidence improves
- extraction revisions should be able to reprocess recent articles cleanly
