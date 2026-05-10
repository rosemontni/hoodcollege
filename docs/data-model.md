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

### `faculty_staff_directory`

Stores official directory entries by Hood profile URL:

- name
- role category
- faculty types
- titles
- phone
- email
- profile URL
- source URL
- first imported date
- last seen in the live directory
- active flag

Directory records are retained historically. A later successful import marks missing profiles inactive rather than deleting them.

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

### Social network analysis report

Planned paths:

- `data/summary/social-network-analysis.md`
- `data/summary/social-network-analysis.json`

Suggested structure:

1. scope note explaining that links are public co-mentions, not private relationships
2. network overview
3. strongest public co-mention bonds
4. most connected people by role
5. faculty public visibility
6. faculty-administration connectors
7. brokerage and articulation people
8. local bridge bonds
9. role mixing
10. emerging people in the last 30 days
11. connected communities

## Record Quality Rules

- every promoted person record must have at least one source article
- every weekly connection must cite article support
- every social network metric must be explainable from article-scoped evidence and include narration about safe interpretation
- ambiguous matches should remain article-scoped until confidence improves
- extraction revisions should be able to reprocess recent articles cleanly
