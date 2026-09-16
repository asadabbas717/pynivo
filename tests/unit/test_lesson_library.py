from pynivo.learning import LessonLibrary


def test_lessons_are_ordered_unique_and_runnable() -> None:
    lessons = LessonLibrary().load()

    assert len(lessons) == 18
    assert [lesson.order for lesson in lessons] == list(range(1, len(lessons) + 1))
    assert len({lesson.identifier for lesson in lessons}) == len(lessons)
    for lesson in lessons:
        assert lesson.explanation and lesson.challenge and lesson.hint and lesson.concepts
        compile(lesson.code, f"<{lesson.identifier}>", "exec")
