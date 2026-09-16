"""Execution request model shared by future process implementations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class ExecutionRequestError(ValueError):
    """Raised when a learner program cannot be safely prepared for launch."""


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    """A structured process launch request that never invokes a command shell."""

    executable: Path
    arguments: tuple[str, ...]
    working_directory: Path

    @classmethod
    def for_script(cls, executable: Path, script: Path) -> ExecutionRequest:
        runtime = executable.expanduser().resolve()
        source_file = script.expanduser().resolve()
        if not runtime.is_file():
            raise ExecutionRequestError(f"Python runtime was not found: {runtime}")
        if not source_file.is_file():
            raise ExecutionRequestError(f"Python file was not found: {source_file}")
        if source_file.suffix.casefold() != ".py":
            raise ExecutionRequestError("PyNivo can only run Python (.py) files")
        return cls(
            executable=runtime,
            arguments=(str(source_file),),
            working_directory=source_file.parent,
        )
