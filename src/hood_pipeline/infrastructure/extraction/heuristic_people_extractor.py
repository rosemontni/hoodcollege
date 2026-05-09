from __future__ import annotations

import re
from collections import OrderedDict

from hood_pipeline.domain.models import PersonMention


class HeuristicPeopleExtractor:
    NAME_PATTERN = re.compile(
        r"\b([A-Z][a-z]+(?:[-'][A-Z][a-z]+)?(?:\s+[A-Z][a-z]+(?:[-'][A-Z][a-z]+)?){1,2})\b"
    )
    BLOCKED_TOKENS = {
        "Academic",
        "Affairs",
        "All-District",
        "All-America",
        "America",
        "Annex",
        "Arena",
        "Atlantic",
        "Athletics",
        "Award",
        "Awards",
        "Basketball",
        "Beneficial-Hodson",
        "Blue",
        "Box",
        "Campus",
        "Career",
        "Center",
        "Centre",
        "Championship",
        "Hood",
        "College",
        "Conference",
        "Contact",
        "County",
        "Cupboard",
        "Day",
        "Department",
        "Director",
        "Division",
        "Earth",
        "Education",
        "Faculty",
        "Field",
        "Final",
        "First",
        "Food",
        "Frederick",
        "General",
        "Golf",
        "Grant",
        "Health",
        "Honor",
        "Inside",
        "Links",
        "Manager",
        "Maryland",
        "Community",
        "Middle",
        "Miss",
        "NCAA",
        "Network",
        "Program",
        "Programs",
        "Office",
        "News",
        "Open",
        "Partnership",
        "Phone",
        "Phoenix",
        "Play",
        "Players",
        "Position",
        "President",
        "Print",
        "Registration",
        "Related",
        "Representative",
        "Round",
        "River",
        "Security",
        "Senior",
        "Senator",
        "Set",
        "Speaker",
        "Spartans",
        "Staff",
        "Stories",
        "Story",
        "Summary",
        "System",
        "Team",
        "Teen",
        "Technology",
        "The",
        "Tickets",
        "Tournament",
        "Version",
        "Video",
        "Videos",
        "Vice",
        "Varsity",
        "Washington",
        "Wilson",
        "Woodsboro",
        "Blazers",
        "Brewers",
        "Hawks",
        "Mid-Distance",
    }
    BLOCKED_PHRASES = (
        "By Mason Cavalier",
        "Media Contact Mason",
        "Cavalier Media Manager",
        "Business Administration",
        "Middle Atlantic Conference",
        "Play Video",
        "Related Stories",
        "Computer Science",
        "Graduate School",
        "Graduate Student",
        "Humanities Sociology",
        "Interdisciplinary Studies",
        "Players Mentioned",
        "Print Friendly Version",
        "First Round",
        "School Counseling",
        "Work Search",
        "Your Future",
        "Teacher Collaboration",
        "Student Research",
        "Student Life",
        "Student English",
        "Save Living",
        "Scholarships Undergraduate",
        "School Biomedical",
        "Residence Life",
        "Publishes Research",
        "On November",
        "Memorial Hall",
        "Marymount University",
        "Monocacy Elementary",
        "National Association",
        "Navy Commander",
        "Task Force",
        "Towson University",
        "Tri-State Association",
        "Virgin Islands",
        "Watershed Studies",
        "Archaeology English",
        "Army Reserve",
        "Blazer Radio",
        "Brodbeck Hall",
        "Coffman Chapel",
        "Colburn School",
        "Creative Writing",
        "Delaplaine School",
        "Different Type",
        "Enhance Pre",
        "Fall Festival",
        "Family Farmer",
        "Following Move-In",
        "Honors Partner",
        "Integrating Art",
        "Leading Colleges",
        "Look Back",
        "Ripley Person",
        "Shrove Tuesday",
        "Souder Named",
        "Students Write",
        "Wisteria Magazine",
    )
    ACADEMIC_PROGRAM_TOKENS = {
        "Administration",
        "Behavior",
        "Business",
        "Clinical",
        "Computer",
        "Counseling",
        "Education",
        "Graduate",
        "Health",
        "Human",
        "Humanities",
        "Interdisciplinary",
        "Mental",
        "Program",
        "Programs",
        "School",
        "Science",
        "Sociology",
        "Staff",
        "Student",
        "Studies",
        "Thanatology",
    }
    PROGRAM_CONTEXT_HINTS = (
        "department",
        "program",
        "graduate school",
        "graduate student",
        "certificate",
        "major",
        "(m.s.)",
        "(b.a.)",
        "(b.s.)",
        "concentration",
    )

    def extract(self, article) -> list[PersonMention]:
        mentions: "OrderedDict[str, PersonMention]" = OrderedDict()

        for context_window in self._context_windows(article.body):
            if len(context_window) < 20:
                continue
            for match in self.NAME_PATTERN.finditer(context_window):
                name = match.group(1).strip()
                local_context = context_window[max(0, match.start() - 80) : match.end() + 80]
                if self._blocked(name, local_context):
                    continue
                if not self._has_context_evidence(name, local_context, article.source_id):
                    continue
                role_category, role_text = self._classify(name, local_context, article.source_id)
                confidence = self._confidence(local_context, role_category)
                if confidence < 0.52:
                    continue
                if name not in mentions:
                    mentions[name] = PersonMention(
                        article_url=article.url,
                        name=name,
                        role_category=role_category,
                        role_text=role_text,
                        context=context_window[:500],
                        confidence=confidence,
                        inclusion_note=f"Matched a plausible full name with nearby role context in {article.source_id}.",
                    )
        return list(mentions.values())

    def _context_windows(self, body: str) -> list[str]:
        windows: list[str] = []
        for block in re.split(r"\n+", body):
            for sentence in re.split(r"(?<=[.!?])\s+", block):
                clean_sentence = " ".join(sentence.split())
                if clean_sentence:
                    windows.append(clean_sentence)
        return windows

    def _blocked(self, name: str, context: str) -> bool:
        if any(phrase in name for phrase in self.BLOCKED_PHRASES):
            return True
        tokens = set(name.split())
        if any(token in self.BLOCKED_TOKENS for token in tokens):
            return True
        if self._looks_like_parenthetical_location_or_school(name, context):
            return True
        if self._looks_like_academic_program(name, context):
            return True
        if name.endswith(" College") or name.endswith(" County"):
            return True
        if len(name.split()) != 2:
            return True
        return False

    def _looks_like_parenthetical_location_or_school(self, name: str, context: str) -> bool:
        escaped_name = re.escape(name)
        return re.search(rf"\([^)()]*/\s*{escaped_name}\)", context) is not None

    def _looks_like_academic_program(self, name: str, context: str) -> bool:
        tokens = name.split()
        if not tokens:
            return False
        if all(token in self.ACADEMIC_PROGRAM_TOKENS for token in tokens):
            lowered_context = context.lower()
            if any(hint in lowered_context for hint in self.PROGRAM_CONTEXT_HINTS):
                return True
        return False

    def _has_context_evidence(self, name: str, context: str, source_id: str) -> bool:
        escaped_name = re.escape(name)
        patterns = (
            rf"(president|dean|provost|representative|senator|director|manager|coordinator|coach|professor)\s+{escaped_name}",
            rf"{escaped_name},\s*(Ph\.D\.|M\.S\.|MBA|DMA|Ed\.D\.|executive director|assistant director|graduate assistant)",
            rf"(said|according to)\s+{escaped_name}",
            rf"{escaped_name}\s*\([^)]+/[^)]+\)",
            rf"{escaped_name}\s+[’']\d{{2}}",
            rf"{escaped_name}.*\b(freshman|junior|senior|student|guard|forward|setter|outside hitter|kills|assists|digs)\b",
        )
        lowered_context = context.lower()
        if source_id.startswith("hood_athletics") and re.search(rf"{escaped_name}\s*\([^)]+\)", context):
            return True
        return any(re.search(pattern, lowered_context, re.IGNORECASE) for pattern in patterns)

    def _classify(self, name: str, context: str, source_id: str) -> tuple[str, str]:
        lowered = context.lower()
        lowered_name = name.lower()
        if f"head coach {lowered_name}" in lowered or f"coach {lowered_name}" in lowered:
            return "coach", "Coach context found near the name."
        if re.search(rf"{re.escape(lowered_name)}.{{0,100}}\b(assistant director of athletics|graduate assistant)\b", lowered):
            return "staff", "Athletics staff title found near the name."
        if re.search(rf"{re.escape(lowered_name)}.{{0,130}}\b(assistant professor|associate professor|visiting assistant professor|professor|instructor)\b", lowered):
            return "faculty", "Academic title found near the name."
        if re.search(rf"{re.escape(lowered_name)}.{{0,130}}\b(provost|dean|vice president|president of hood|hood'?s .* president)\b", lowered):
            return "administrator", "Senior academic or administrative title found near the name."
        if re.search(rf"\b(board chair|hood.?s own president|hood college president|dean|provost|vice president).{{0,80}}{re.escape(lowered_name)}\b", lowered):
            return "administrator", "Senior academic or administrative title found near the name."
        if re.search(rf"{re.escape(lowered_name)}.{{0,100}}\bsenior (climate )?advisor\b", lowered):
            return "guest", "External advisor context found near the name."
        if self._student_leadership_context(lowered, lowered_name):
            return "student", "Student leadership context found near the name."
        if any(f"{title} {lowered_name}" in lowered for title in ("president", "dean", "vice president")):
            return "administrator", "Senior academic or administrative title found near the name."
        if any(f"{title} {lowered_name}" in lowered for title in ("professor", "lecturer", "chair")):
            return "faculty", "Academic title found near the name."
        if any(
            f"{title} {lowered_name}" in lowered
            for title in ("executive director", "director", "manager", "coordinator")
        ):
            return "staff", "Operational staff title found near the name."
        if any(keyword in lowered for keyword in ("alumn", "'12", "'13", "'14", "'15", "'16", "'17", "'18")):
            return "alumni", "Alumni marker found near the name."
        if any(keyword in lowered for keyword in ("freshman", "senior", "junior", "major", "student", "guard", "forward", "setter", "outside hitter")):
            return "student", "Student context found near the name."
        if source_id.startswith("hood_athletics"):
            return "student-athlete", "Athletics source implies student-athlete context."
        return "person", "General person mention."

    def _student_leadership_context(self, lowered_context: str, lowered_name: str) -> bool:
        class_president_patterns = (
            f"senior class president {lowered_name}",
            f"class president {lowered_name}",
            f"student government president {lowered_name}",
            f"{lowered_name}, president of the class",
            f"{lowered_name}, president of class",
            f"{lowered_name}, senior class president",
            f"{lowered_name}, class president",
        )
        return any(pattern in lowered_context for pattern in class_president_patterns)

    def _confidence(self, context: str, role_category: str) -> float:
        score = 0.52
        lowered = context.lower()
        if any(keyword in lowered for keyword in ("said", "quote", "according to", "scored", "recorded")):
            score += 0.08
        if role_category != "person":
            score += 0.1
        if len(context) > 60:
            score += 0.05
        return min(score, 0.92)
