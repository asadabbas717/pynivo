"""Python source editor with line numbers and automatic indentation."""

from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFontDatabase, QKeyEvent, QPainter, QPaintEvent, QTextFormat
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

from pynivo.ui.editor.highlighter import PythonHighlighter


class LineNumberArea(QWidget):
    def __init__(self, editor: CodeEditor) -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(self.editor.line_number_width(), 0)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        self.editor.paint_line_numbers(event)


class CodeEditor(QPlainTextEdit):
    """A focused code widget whose parent owns document lifecycle."""

    INDENT = "    "

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.line_numbers = LineNumberArea(self)
        self.highlighter = PythonHighlighter(self.document())
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabChangesFocus(False)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(11)
        self.setFont(font)
        self.blockCountChanged.connect(self._update_margin)
        self.updateRequest.connect(self._update_line_numbers)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self._update_margin()
        self._highlight_current_line()

    def line_number_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_margin(self) -> None:
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)

    def _update_line_numbers(self, rect: QRect, delta: int) -> None:
        if delta:
            self.line_numbers.scroll(0, delta)
        else:
            self.line_numbers.update(0, rect.y(), self.line_numbers.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_margin()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        contents = self.contentsRect()
        self.line_numbers.setGeometry(
            QRect(contents.left(), contents.top(), self.line_number_width(), contents.height())
        )

    def paint_line_numbers(self, event: QPaintEvent) -> None:
        painter = QPainter(self.line_numbers)
        painter.fillRect(event.rect(), QColor("#F2F4F7"))
        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        painter.setPen(QColor("#667085"))
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.drawText(
                    0,
                    top,
                    self.line_numbers.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            number += 1

    def _highlight_current_line(self) -> None:
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor("#F7F8FC"))
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Tab and not event.modifiers():
            self.insertPlainText(self.INDENT)
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current_line = self.textCursor().block().text()
            leading = current_line[: len(current_line) - len(current_line.lstrip())]
            if current_line.rstrip().endswith(":"):
                leading += self.INDENT
            super().keyPressEvent(event)
            self.insertPlainText(leading)
            return
        super().keyPressEvent(event)
