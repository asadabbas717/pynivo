"""Course progress model independent from the Qt settings adapter."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CourseProgress:
    completed: frozenset[str] = frozenset()

    def mark_complete(self, lesson_id: str) -> CourseProgress:
        return CourseProgress(self.completed | {lesson_id})

    def percentage(self, total_lessons: int) -> int:
        if total_lessons <= 0:
            return 0
        return round(min(len(self.completed), total_lessons) / total_lessons * 100)
