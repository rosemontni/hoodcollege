# Hood College Signal Atlas

Hood College Signal Atlas is a planning-first repository for a daily intelligence pipeline focused on **Hood College in Frederick, Maryland**.

The project goal is to:

1. collect new Hood College coverage each day from carefully chosen sources
2. extract the people mentioned in that coverage
3. store role-aware person records with article evidence and traceable provenance
4. publish a short markdown discovery story each day
5. publish a weekly relationship report describing meaningful connections between the people observed

This repository is intentionally starting with planning and documentation before implementation.

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

## Planned Outputs

- daily article intake records
- daily person mention records
- daily markdown discovery stories
- weekly connection summaries
- a local database that preserves article-level evidence

## Planning Docs

- [docs/project-plan.md](docs/project-plan.md)
- [docs/source-strategy.md](docs/source-strategy.md)
- [docs/data-model.md](docs/data-model.md)

## Repository Metadata

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [CODEOWNERS](CODEOWNERS)

## Current Status

Planning baseline complete.
Implementation work will begin in the next phase.
