from __future__ import annotations

from urllib.parse import urlparse


class HoodDisambiguator:
    POSITIVE_MARKERS = (
        "hood college",
        "frederick, maryland",
        "frederick, md",
        "401 rosemont",
        "blazers",
    )
    NEGATIVE_MARKERS = (
        "hood theological seminary",
        "hood river",
        "robin hood",
        "ticketsmarter",
        "entertainment guide",
    )

    def evaluate(self, article) -> tuple[bool, str]:
        parsed = urlparse(article.url)
        domain = parsed.netloc.lower()
        combined = f"{article.title}\n{article.body}".lower()

        for marker in self.NEGATIVE_MARKERS:
            if marker in combined:
                return False, f"Rejected because it matched negative marker '{marker}'."

        if domain == "hoodathletics.com":
            if "tickets" in combined and "hood college blazers" not in combined:
                return False, "Rejected athletics item because it resembled ticket or entertainment copy."
            return True, "Accepted because the article came from Hood Athletics."

        if domain == "www.hood.edu":
            if parsed.path.startswith("/news/"):
                return True, "Accepted because the article came from Hood College News."
            if parsed.path.startswith("/discover/stories/"):
                return True, "Accepted because the article came from official Hood College Stories."

        if any(marker in combined for marker in self.POSITIVE_MARKERS):
            return True, "Accepted because the article contained Hood/Frederick campus markers."

        return False, "Rejected because the article lacked strong Hood College disambiguation signals."
