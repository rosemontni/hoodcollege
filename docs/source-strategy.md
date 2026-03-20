# Source And Disambiguation Strategy

## Identity Target

This project covers **Hood College in Frederick, Maryland** only.

The strongest positive disambiguation signals are:

- `hood.edu`
- `hoodathletics.com`
- article text explicitly naming `Hood College`
- article text explicitly naming `Frederick, Md.` or `Frederick, Maryland`
- article text referencing `401 Rosemont Ave.`
- article text referencing known Hood context such as the Blazers, campus buildings, academic programs, or Hood College offices

## Early Source Tiers

### Tier 1: official institutional sources

- `https://www.hood.edu/news`
- `https://www.hood.edu/campus-events`
- official Hood pages for named campus programs, talks, theatre, and academic initiatives when they publish person-rich updates

### Tier 2: official athletics sources

- `https://hoodathletics.com/news`
- team pages and recaps that identify student-athletes, coaches, and athletics staff

### Tier 3: selective local media

This tier should wait until the official-source pipeline is stable. Candidate local sources can be added later if they regularly mention Hood College in Frederick with article-level clarity.

## Negative Disambiguation Signals

Reject or down-rank items when the page refers to:

- another institution with `Hood` in the name
- non-college organizations, businesses, or places named `Hood`
- articles lacking any Frederick or Hood College campus context
- result pages, tag pages, schedule pages, or roster indexes with no article narrative

## Article Inclusion Rules

An article is eligible when it satisfies at least one strong Hood-specific signal and does not trigger a negative disambiguation rule.

Preferred article types:

- institutional news releases
- campus event announcements or recaps
- athletics recaps and athlete recognition stories
- academic program spotlights
- partnership announcements
- faculty expert features
- student achievement stories

## Person Categories To Capture

- student
- student-athlete
- faculty
- staff
- administrator
- alumnus or alumna
- board member
- guest speaker
- visitor
- community partner
- donor
- coach
- recruiter or admissions contact

## Per-Person Capture Rules

For each person mention, record:

- full displayed name
- role category
- article-specific role text
- department, office, team, program, class year, major, or hometown when present
- source article URL
- publication date
- short note describing how the person appears in the article

## Storytelling Rule

Daily discovery writing should read like a short factual story, not a bullet dump. It should connect people through the events, programs, games, recognitions, and partnerships that brought them into the day’s coverage.

## Connection Rule

Weekly connection discovery should be evidence-led. Favor:

- co-appearance in the same article
- shared department or office
- shared athletic team
- shared academic program
- shared event participation
- direct quote or stated relationship

Avoid speculative connections based only on name proximity.
