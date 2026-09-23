from pynivo.ui.editor.text_tools import indent_lines, matching_bracket, unindent_lines


def test_matching_bracket_handles_nesting_and_both_directions() -> None:
    text = "call(items[0])"

    assert matching_bracket(text, 4) == 13
    assert matching_bracket(text, 13) == 4
    assert matching_bracket(text, 10) == 12
    assert matching_bracket(text, 0) is None


def test_indent_and_unindent_multiple_lines() -> None:
    original = "first\n    second\nthird"

    assert indent_lines(original) == "    first\n        second\n    third"
    assert unindent_lines(original) == "first\nsecond\nthird"
