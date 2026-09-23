"""Pure text helpers used by the Qt editor."""

BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}"}
REVERSE_PAIRS = {closing: opening for opening, closing in BRACKET_PAIRS.items()}


def matching_bracket(text: str, position: int) -> int | None:
    if position < 0 or position >= len(text):
        return None
    bracket = text[position]
    if bracket in BRACKET_PAIRS:
        expected = BRACKET_PAIRS[bracket]
        depth = 0
        for index in range(position + 1, len(text)):
            if text[index] == bracket:
                depth += 1
            elif text[index] == expected:
                if depth == 0:
                    return index
                depth -= 1
    elif bracket in REVERSE_PAIRS:
        expected = REVERSE_PAIRS[bracket]
        depth = 0
        for index in range(position - 1, -1, -1):
            if text[index] == bracket:
                depth += 1
            elif text[index] == expected:
                if depth == 0:
                    return index
                depth -= 1
    return None


def indent_lines(text: str, indent: str = "    ") -> str:
    return "\n".join(f"{indent}{line}" for line in text.split("\n"))


def unindent_lines(text: str, indent_size: int = 4) -> str:
    result = []
    for line in text.split("\n"):
        remove = min(len(line) - len(line.lstrip(" ")), indent_size)
        result.append(line[remove:])
    return "\n".join(result)
