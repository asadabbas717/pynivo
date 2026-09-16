"""Abstractions for locating a Python runtime used to execute learner code."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RuntimeInfo:
    """Validated information about an available Python runtime."""

    executable: Path
    version: str


class RuntimeManager(Protocol):
    """Contract implemented by development and bundled runtime managers."""

    def locate_runtime(self) -> Path | None:
        """Return a candidate Python executable, if one is available."""

    def validate_runtime(self, executable: Path) -> RuntimeInfo:
        """Validate an executable and return its runtime information."""


class RuntimeValidationError(RuntimeError):
    """Raised when a candidate runtime cannot be used by PyNivo."""


class SystemRuntimeManager:
    """Development runtime manager backed by the interpreter running PyNivo."""

    _VALIDATION_TIMEOUT_SECONDS = 5

    def locate_runtime(self) -> Path | None:
        executable = Path(sys.executable)
        return executable if executable.is_file() else None

    def validate_runtime(self, executable: Path) -> RuntimeInfo:
        candidate = executable.expanduser().resolve()
        if not candidate.is_file():
            raise RuntimeValidationError(f"Python runtime was not found: {candidate}")

        try:
            result = subprocess.run(
                [str(candidate), "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self._VALIDATION_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise RuntimeValidationError(f"Could not start Python runtime: {candidate}") from error

        version = (result.stdout or result.stderr).strip()
        if result.returncode != 0 or not version.startswith("Python "):
            raise RuntimeValidationError(f"Executable is not a valid Python runtime: {candidate}")
        return RuntimeInfo(executable=candidate, version=version.removeprefix("Python "))


class BundledRuntimeManager(SystemRuntimeManager):
    """Locate and validate PyNivo's private Windows CPython runtime."""

    def __init__(self, application_root: Path) -> None:
        self.runtime_root = application_root / "runtime"

    def locate_runtime(self) -> Path | None:
        executable = self.runtime_root / "python.exe"
        return executable if executable.is_file() else None

    def validate_runtime(self, executable: Path) -> RuntimeInfo:
        if executable.resolve().parent != self.runtime_root.resolve():
            raise RuntimeValidationError("Bundled Python must be inside PyNivo's runtime folder")
        if not any(self.runtime_root.glob("python*.zip")):
            raise RuntimeValidationError("Bundled Python standard library archive is missing")
        if not any(self.runtime_root.glob("python3*.dll")):
            raise RuntimeValidationError("Bundled Python DLL is missing")
        if not any(self.runtime_root.glob("python*._pth")):
            raise RuntimeValidationError("Bundled Python isolation configuration is missing")
        return super().validate_runtime(executable)


class RuntimeResolver:
    """Prefer a bundled runtime, falling back to development Python when absent."""

    def __init__(self, application_root: Path) -> None:
        self.bundled = BundledRuntimeManager(application_root)
        self.system = SystemRuntimeManager()

    def locate_runtime(self) -> Path | None:
        return self.bundled.locate_runtime() or self.system.locate_runtime()

    def validate_runtime(self, executable: Path) -> RuntimeInfo:
        bundled = self.bundled.locate_runtime()
        manager = (
            self.bundled if bundled and executable.resolve() == bundled.resolve() else self.system
        )
        return manager.validate_runtime(executable)
