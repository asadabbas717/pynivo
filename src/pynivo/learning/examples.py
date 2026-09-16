"""Validated access to bundled beginner examples."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files


@dataclass(frozen=True, slots=True)
class Example:
    identifier: str
    title: str
    category: str
    description: str
    code: str


class ExampleLibrary:
    """Load examples bundled inside the installed PyNivo package."""

    def load(self) -> tuple[Example, ...]:
        resource = files("pynivo.learning.data").joinpath("examples.json")
        records = json.loads(resource.read_text(encoding="utf-8"))
        examples = tuple(Example(**record) for record in records)
        identifiers = [example.identifier for example in examples]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Example identifiers must be unique")
        return examples
