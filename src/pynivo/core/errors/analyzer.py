"""Parse Python tracebacks into beginner-friendly structured errors."""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import get_close_matches


@dataclass(frozen=True, slots=True)
class PythonError:
    exception_type: str
    message: str
    filename: str | None
    line_number: int | None
    source_line: str | None
    traceback: str
    explanation: str
    suggestions: tuple[str, ...] = ()


class ErrorAnalyzer:
    _location = re.compile(r'^\s*File "(?P<file>.+)", line (?P<line>\d+)')
    _exception = re.compile(r"^(?P<type>[A-Za-z_][\w.]*(?:Error|Exception)):\s*(?P<message>.*)$")
    _explanations = {
        "SyntaxError": "Python could not understand this code. Check punctuation and spelling.",
        "IndentationError": "The spaces at the start of this line do not match its structure.",
        "NameError": "Python does not recognize this name. Check its spelling and definition.",
        "TypeError": "An operation received a kind of value it cannot use in that way.",
        "ValueError": "A value has the right type, but its contents are not acceptable here.",
        "IndexError": "The program tried to access a list position that does not exist.",
        "KeyError": "The program tried to use a dictionary key that does not exist.",
        "ZeroDivisionError": "A number cannot be divided by zero.",
        "ModuleNotFoundError": "Python could not find this module. It may not be installed.",
    }

    def analyze(self, traceback: str, source_code: str = "") -> PythonError | None:
        lines = traceback.rstrip().splitlines()
        exception_match = next(
            (match for line in reversed(lines) if (match := self._exception.match(line.strip()))),
            None,
        )
        if exception_match is None:
            return None
        locations = [match for line in lines if (match := self._location.match(line))]
        location = locations[-1] if locations else None
        source_line = None
        if location:
            location_index = next(i for i, line in enumerate(lines) if line == location.string)
            if location_index + 1 < len(lines):
                candidate = lines[location_index + 1].strip()
                if candidate and not candidate.startswith("^"):
                    source_line = candidate
        exception_type = exception_match.group("type")
        suggestions = self._suggestions(
            exception_type, exception_match.group("message"), source_code
        )
        return PythonError(
            exception_type=exception_type,
            message=exception_match.group("message"),
            filename=location.group("file") if location else None,
            line_number=int(location.group("line")) if location else None,
            source_line=source_line,
            traceback=traceback,
            explanation=self._explanations.get(
                exception_type, "Python stopped because the program raised an error."
            ),
            suggestions=suggestions,
        )

    def format_beginner_message(self, error: PythonError) -> str:
        location = f" — line {error.line_number}" if error.line_number else ""
        result = f"\n{error.exception_type}{location}\n\n{error.explanation}\n"
        if error.message:
            result += f"\nPython says: {error.message}\n"
        if error.suggestions:
            result += f'\nDid you mean "{error.suggestions[0]}"?\n'
        return result

    def _suggestions(self, exception_type: str, message: str, source_code: str) -> tuple[str, ...]:
        if exception_type != "NameError" or not source_code:
            return ()
        missing = re.search(r"name ['\"](?P<name>[A-Za-z_]\w*)['\"] is not defined", message)
        if not missing:
            return ()
        unknown = missing.group("name")
        identifiers = set(re.findall(r"\b[A-Za-z_]\w*\b", source_code))
        identifiers.discard(unknown)
        matches = get_close_matches(unknown, identifiers, n=3, cutoff=0.72)
        return tuple(matches)
