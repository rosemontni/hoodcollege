from __future__ import annotations

from pathlib import Path


class BuildPagesSiteService:
    def __init__(self, services) -> None:
        self.services = services

    def run(self, output_dir: Path) -> str:
        return self.services.pages_writer.build_site(output_dir)
