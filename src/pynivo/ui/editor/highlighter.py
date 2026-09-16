"""Lightweight Python syntax highlighting using Qt only."""

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextDocument


def _text_format(color: str, *, bold: bool = False, italic: bool = False) -> QTextCharFormat:
    result = QTextCharFormat()
    result.setForeground(QColor(color))
    result.setFontItalic(italic)
    if bold:
        result.setFontWeight(QFont.Weight.Bold)
    return result


class PythonHighlighter(QSyntaxHighlighter):
    """Highlight common Python tokens without a parser dependency."""

    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self.set_colors(("#C792EA", "#4DD7FA", "#F9C74F", "#60788A", "#5FFFB0"))

    def set_colors(self, colors: tuple[str, str, str, str, str]) -> None:
        keywords = (
            "and|as|assert|async|await|break|class|continue|def|del|elif|else|except|False|"
            "finally|for|from|global|if|import|in|is|lambda|None|nonlocal|not|or|pass|raise|"
            "return|True|try|while|with|yield"
        )
        self._rules = (
            (QRegularExpression(rf"\b(?:{keywords})\b"), _text_format(colors[0], bold=True)),
            (
                QRegularExpression(
                    r"\b(?:print|input|len|range|str|int|float|list|dict|set|tuple)\b"
                ),
                _text_format(colors[1]),
            ),
            (QRegularExpression(r"\b\d+(?:\.\d+)?\b"), _text_format(colors[2])),
            (QRegularExpression(r"#[^\n]*"), _text_format(colors[3], italic=True)),
            (
                QRegularExpression(r"""(?:[rubfRUBF]{0,2})(?:"[^"\n]*"|'[^'\n]*')"""),
                _text_format(colors[4]),
            ),
        )
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:  # noqa: N802
        for expression, text_format in self._rules:
            matches = expression.globalMatch(text)
            while matches.hasNext():
                match = matches.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), text_format)
