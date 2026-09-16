"""Validated access to PyNivo's bundled offline curriculum."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files


@dataclass(frozen=True, slots=True)
class Lesson:
    identifier: str
    order: int
    title: str
    explanation: str
    code: str
    challenge: str
    hint: str
    concepts: tuple[str, ...]


class LessonLibrary:
    def load(self) -> tuple[Lesson, ...]:
        resource = files("pynivo.learning.data").joinpath("lessons.json")
        records = json.loads(resource.read_text(encoding="utf-8"))
        lessons = tuple(
            Lesson(**{**record, "concepts": tuple(record["concepts"])}) for record in records
        )
        if len({lesson.identifier for lesson in lessons}) != len(lessons):
            raise ValueError("Lesson identifiers must be unique")
        if [lesson.order for lesson in lessons] != sorted(lesson.order for lesson in lessons):
            raise ValueError("Lessons must be stored in curriculum order")
        return lessons
