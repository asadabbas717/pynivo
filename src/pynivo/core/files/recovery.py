"""Local recovery snapshots for unsaved learner documents."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RecoveryDocument:
    path: str | None
    text: str


class RecoveryService:
    """Persist one atomic session snapshot without touching source files."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.snapshot_path = directory / "session.json"

    def save(self, documents: tuple[RecoveryDocument, ...]) -> None:
        if not documents:
            self.clear()
            return
        self.directory.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        try:
            descriptor, name = tempfile.mkstemp(
                prefix="session.", suffix=".tmp", dir=self.directory
            )
            temporary = Path(name)
            payload = {"version": 1, "documents": [asdict(document) for document in documents]}
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(payload, handle, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.snapshot_path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def load(self) -> tuple[RecoveryDocument, ...]:
        if not self.snapshot_path.is_file():
            return ()
        try:
            payload = json.loads(self.snapshot_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or type(payload.get("version")) is not int:
                return ()
            if payload["version"] != 1 or not isinstance(payload.get("documents"), list):
                return ()
            return tuple(
                RecoveryDocument(path=item.get("path"), text=item["text"])
                for item in payload.get("documents", [])
                if isinstance(item, dict)
                and isinstance(item.get("text"), str)
                and (item.get("path") is None or isinstance(item.get("path"), str))
                and "\x00" not in (item.get("path") or "")
            )
        except (OSError, ValueError, TypeError, KeyError):
            return ()

    def clear(self) -> None:
        self.snapshot_path.unlink(missing_ok=True)
