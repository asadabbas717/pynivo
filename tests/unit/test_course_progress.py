from pynivo.learning import CourseProgress


def test_course_progress_is_immutable_and_calculates_percentage() -> None:
    empty = CourseProgress()
    started = empty.mark_complete("hello_world")

    assert empty.completed == frozenset()
    assert started.completed == frozenset({"hello_world"})
    assert started.mark_complete("hello_world") == started
    assert started.percentage(4) == 25
    assert empty.percentage(0) == 0
