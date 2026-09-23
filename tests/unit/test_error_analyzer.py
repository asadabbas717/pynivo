from pynivo.core.errors import ErrorAnalyzer


def test_parses_name_error_with_location_and_source() -> None:
    traceback = """Traceback (most recent call last):
  File "C:\\lessons\\hello.py", line 4, in <module>
    print(usernme)
          ^^^^^^^^
NameError: name 'usernme' is not defined
"""
    error = ErrorAnalyzer().analyze(traceback)

    assert error is not None
    assert error.exception_type == "NameError"
    assert error.line_number == 4
    assert error.source_line == "print(usernme)"
    assert "does not recognize" in error.explanation
    assert error.traceback == traceback


def test_parses_syntax_error() -> None:
    traceback = """  File "broken.py", line 1
    if True
           ^
SyntaxError: expected ':'
"""
    error = ErrorAnalyzer().analyze(traceback)
    assert error is not None
    assert error.exception_type == "SyntaxError"
    assert error.line_number == 1


def test_returns_none_for_non_traceback_text() -> None:
    assert ErrorAnalyzer().analyze("ordinary stderr output") is None


def test_suggests_close_name_from_source() -> None:
    traceback = """Traceback (most recent call last):
  File "hello.py", line 2, in <module>
    print(usernme)
NameError: name 'usernme' is not defined
"""
    error = ErrorAnalyzer().analyze(traceback, 'username = "Ada"\nprint(usernme)\n')

    assert error is not None
    assert error.suggestions == ("username",)
    assert 'Did you mean "username"?' in ErrorAnalyzer().format_beginner_message(error)
