from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AppConfig:
    repo_root: Path
    sources_path: Path
    data_dir: Path
    discoveries_dir: Path
    connections_dir: Path
    directory_dir: Path
    monthly_reports_dir: Path
    summary_dir: Path
    database_path: Path
    user_agent: str
    request_timeout_seconds: int

    @classmethod
    def load(cls) -> "AppConfig":
        repo_root = _repo_root()
        data_dir = repo_root / "data"
        discoveries_dir = data_dir / "discoveries"
        connections_dir = data_dir / "connections"
        directory_dir = data_dir / "directory"
        monthly_reports_dir = data_dir / "monthly"
        summary_dir = data_dir / "summary"
        database_path = data_dir / "hood_people.db"
        sources_path = repo_root / "sources" / "hood_sources.json"
        user_agent = os.getenv(
            "HOOD_PIPELINE_USER_AGENT",
            "HoodCollegeSignalAtlas/0.1 (+https://github.com/rosemontni/hoodcollege)",
        )
        timeout = int(os.getenv("HOOD_PIPELINE_REQUEST_TIMEOUT", "20"))
        return cls(
            repo_root=repo_root,
            sources_path=Path(os.getenv("HOOD_PIPELINE_SOURCES_PATH", sources_path)),
            data_dir=Path(os.getenv("HOOD_PIPELINE_DATA_DIR", data_dir)),
            discoveries_dir=Path(os.getenv("HOOD_PIPELINE_DISCOVERIES_DIR", discoveries_dir)),
            connections_dir=Path(os.getenv("HOOD_PIPELINE_CONNECTIONS_DIR", connections_dir)),
            directory_dir=Path(os.getenv("HOOD_PIPELINE_DIRECTORY_DIR", directory_dir)),
            monthly_reports_dir=Path(os.getenv("HOOD_PIPELINE_MONTHLY_REPORTS_DIR", monthly_reports_dir)),
            summary_dir=Path(os.getenv("HOOD_PIPELINE_SUMMARY_DIR", summary_dir)),
            database_path=Path(os.getenv("HOOD_PIPELINE_DATABASE_PATH", database_path)),
            user_agent=user_agent,
            request_timeout_seconds=timeout,
        )

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.discoveries_dir.mkdir(parents=True, exist_ok=True)
        self.connections_dir.mkdir(parents=True, exist_ok=True)
        self.directory_dir.mkdir(parents=True, exist_ok=True)
        self.monthly_reports_dir.mkdir(parents=True, exist_ok=True)
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def load_source_definitions(self) -> list[dict[str, object]]:
        with self.sources_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            raise ValueError("Source configuration must be a list.")
        return payload
