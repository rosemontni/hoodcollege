from __future__ import annotations

import re
from datetime import date
from urllib.parse import urlencode, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

from hood_pipeline.domain.models import FacultyStaffRecord


FACULTY_TYPES = {
    "Undergraduate Faculty",
    "Graduate Faculty",
    "Emeritus Faculty",
    "Emeritus",
}


class HoodFacultyDirectoryReader:
    def __init__(self, fetcher) -> None:
        self.fetcher = fetcher

    def read(self, source_url: str, imported_at: date, max_pages: int = 25) -> list[FacultyStaffRecord]:
        records_by_profile_url: dict[str, FacultyStaffRecord] = {}
        for page_index in range(max_pages):
            page_url = self._page_url(source_url, page_index)
            html = self.fetcher.fetch_text(page_url)
            page_records = self.parse_page(html, page_url, imported_at)
            if not page_records:
                break
            for record in page_records:
                records_by_profile_url[record.profile_url] = record
        return sorted(records_by_profile_url.values(), key=lambda item: item.name.lower())

    def parse_page(self, html: str, source_url: str, imported_at: date) -> list[FacultyStaffRecord]:
        soup = BeautifulSoup(html, "html.parser")
        records: list[FacultyStaffRecord] = []
        containers = soup.select(".faculty__listing__member")
        if containers:
            for container in containers:
                heading = container.find("h2")
                if heading is None:
                    continue
                record = self._record_from_heading(
                    heading,
                    self._container_lines(container),
                    source_url,
                    imported_at,
                )
                if record is not None:
                    records.append(record)
            return records

        for heading in soup.find_all("h2"):
            record = self._record_from_heading(
                heading,
                self._profile_lines(heading),
                source_url,
                imported_at,
            )
            if record is not None:
                records.append(record)
        return records

    def _record_from_heading(
        self,
        heading,
        lines: list[str],
        source_url: str,
        imported_at: date,
    ) -> FacultyStaffRecord | None:
        link = heading.find("a", href=True)
        raw_name = heading.get_text(" ", strip=True)
        if not link or not raw_name:
            return None
        lines = [line for line in lines if line != raw_name]
        faculty_types = [line for line in lines if line in FACULTY_TYPES]
        if not faculty_types:
            return None
        profile_url = urljoin(source_url, str(link["href"]))
        titles = self._titles(lines)
        return FacultyStaffRecord(
            name=self._clean_name(raw_name),
            role_category=self._role_category(faculty_types, titles),
            faculty_types=faculty_types,
            titles=titles,
            phone=self._field_after_label(lines, "Phone"),
            email=self._field_after_label(lines, "Email"),
            profile_url=profile_url,
            source_url=source_url,
            imported_at=imported_at,
            last_seen_in_directory=imported_at,
            active=True,
        )

    def _container_lines(self, container) -> list[str]:
        lines: list[str] = []
        text = container.get_text("\n", strip=True)
        for line in text.splitlines():
            cleaned = " ".join(line.split())
            if cleaned:
                lines.append(cleaned)
        return lines

    def _profile_lines(self, heading) -> list[str]:
        lines: list[str] = []
        for sibling in heading.next_siblings:
            if getattr(sibling, "name", None) in {"h1", "h2", "h3", "h4"}:
                break
            text = sibling.get_text("\n", strip=True) if hasattr(sibling, "get_text") else str(sibling).strip()
            for line in text.splitlines():
                cleaned = " ".join(line.split())
                if cleaned:
                    lines.append(cleaned)
        return lines

    def _titles(self, lines: list[str]) -> list[str]:
        titles: list[str] = []
        stop_labels = {"Phone", "Email"}
        for line in lines:
            if line in FACULTY_TYPES or line in stop_labels:
                continue
            if "@" in line:
                continue
            if re.fullmatch(r"(N/A|x+|[0-9xX(). -]+)", line):
                continue
            if line.lower() == "no office phone":
                continue
            if line.lower().endswith("pronouns"):
                continue
            titles.append(line)
        return titles

    def _field_after_label(self, lines: list[str], label: str) -> str:
        for index, line in enumerate(lines):
            if line != label:
                continue
            for candidate in lines[index + 1 :]:
                if candidate in {"Phone", "Email"}:
                    return ""
                return candidate
        return ""

    def _clean_name(self, raw_name: str) -> str:
        cleaned = re.sub(
            r",\s*(Ph\.D\.|M\.S\.|M\.A\.|M\.Ed\.|MBA|DNP|Ed\.D\.|DMA|D\.Sc\.|RN|CHSE)(?:,\s*[A-Z-]+)*$",
            "",
            raw_name,
        )
        return " ".join(cleaned.split())

    def _role_category(self, faculty_types: list[str], titles: list[str]) -> str:
        joined_titles = " ".join(titles).lower()
        if "dean" in joined_titles:
            return "administrator"
        if any("faculty" in faculty_type.lower() for faculty_type in faculty_types):
            return "faculty"
        return "staff"

    def _page_url(self, source_url: str, page_index: int) -> str:
        if page_index == 0:
            return source_url
        parsed = urlparse(source_url)
        query = urlencode({"page": page_index})
        return urlunparse(parsed._replace(query=query))
