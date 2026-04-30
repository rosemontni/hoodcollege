from __future__ import annotations

from datetime import date

from hood_pipeline.domain.models import FacultyStaffImportResult


class FacultyStaffImportService:
    SOURCE_URL = "https://www.hood.edu/academics/faculty"

    def __init__(self, services) -> None:
        self.services = services

    def run(self, run_date: date, source_url: str | None = None) -> FacultyStaffImportResult:
        directory_url = source_url or self.SOURCE_URL
        records = self.services.faculty_directory_reader.read(directory_url, run_date)
        self.services.sqlite.replace_faculty_staff_directory(records)
        retained_records = self.services.sqlite.faculty_staff_directory()
        report_path = self.services.directory_writer.write_faculty_staff_directory(
            run_date,
            directory_url,
            retained_records,
        )
        return FacultyStaffImportResult(
            run_date=run_date,
            source_url=directory_url,
            records=records,
            report_path=report_path,
        )
