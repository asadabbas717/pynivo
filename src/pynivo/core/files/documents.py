"""UI-independent loading and atomic saving of Python source files."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


class DocumentError(OSError):
    """Raised when a source document cannot be read or written safely."""


@dataclass(frozen=True, slots=True)
class Document:
    path: Path
    text: str


class DocumentService:
    """Read UTF-8 Python files and replace them atomically when saving."""

    def load(self, path: Path) -> Document:
        source = path.expanduser().resolve()
        if source.suffix.casefold() != ".py":
            raise DocumentError("PyNivo can only open Python (.py) files")
        try:
            text = source.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            raise DocumentError(f"Could not open {source.name}: {error}") from error
        return Document(path=source, text=text)

    def save(self, path: Path, text: str) -> Document:
        destination = path.expanduser().resolve()
        if destination.suffix.casefold() != ".py":
            destination = destination.with_suffix(".py")
        if not destination.parent.is_dir():
            raise DocumentError(f"Folder does not exist: {destination.parent}")

        temporary: Path | None = None
        try:
            descriptor, name = tempfile.mkstemp(
                prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
            )
            temporary = Path(name)
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, destination)
        except (OSError, UnicodeError) as error:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            raise DocumentError(f"Could not save {destination.name}: {error}") from error
        return Document(path=destination, text=text)
