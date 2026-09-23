"""Python source editor with line numbers and automatic indentation."""

from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFontDatabase,
    QKeyEvent,
    QPainter,
    QPaintEvent,
    QTextCursor,
    QTextFormat,
)
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

from pynivo.ui.editor.highlighter import PythonHighlighter
from pynivo.ui.editor.text_tools import indent_lines, matching_bracket, unindent_lines
from pynivo.ui.themes import DARK, Theme


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
        self.theme = DARK
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabChangesFocus(False)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(11)
        self.setFont(font)
        self.blockCountChanged.connect(self._update_margin)
        self.updateRequest.connect(self._update_line_numbers)
        self.cursorPositionChanged.connect(self._update_extra_selections)
        self._update_margin()
        self._update_extra_selections()

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
        painter.fillRect(event.rect(), QColor(self.theme.gutter_background))
        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        painter.setPen(QColor(self.theme.gutter_text))
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

    def _update_extra_selections(self) -> None:
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor(self.theme.current_line))
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        selections = [selection]
        cursor = self.textCursor()
        document_text = self.toPlainText()
        candidates = (cursor.position() - 1, cursor.position())
        for position in candidates:
            match = matching_bracket(document_text, position)
            if match is not None:
                for bracket_position in (position, match):
                    bracket = QTextEdit.ExtraSelection()
                    bracket.cursor = self.textCursor()
                    bracket.cursor.setPosition(bracket_position)
                    bracket.cursor.movePosition(
                        QTextCursor.MoveOperation.Right,
                        QTextCursor.MoveMode.KeepAnchor,
                    )
                    bracket.format.setBackground(QColor("#007F6F"))
                    bracket.format.setForeground(QColor("#FFFFFF"))
                    selections.append(bracket)
                break
        self.setExtraSelections(selections)

    def set_theme(self, theme: Theme) -> None:
        self.theme = theme
        self.highlighter.set_colors(theme.syntax)
        self.line_numbers.update()
        self._update_extra_selections()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
            unindent = event.key() == Qt.Key.Key_Backtab or bool(
                event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            )
            self._change_indentation(unindent=unindent)
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

    def _change_indentation(self, *, unindent: bool) -> None:
        cursor = self.textCursor()
        if not cursor.hasSelection():
            if unindent:
                leading_spaces = len(cursor.block().text()) - len(cursor.block().text().lstrip(" "))
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.KeepAnchor,
                    min(len(self.INDENT), leading_spaces),
                )
                cursor.removeSelectedText()
            else:
                cursor.insertText(self.INDENT)
            return
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        start = cursor.position()
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        if cursor.atBlockStart() and end > start:
            cursor.movePosition(
                QTextCursor.MoveOperation.Left,
                QTextCursor.MoveMode.KeepAnchor,
            )
        selected = cursor.selectedText().replace("\u2029", "\n")
        replacement = unindent_lines(selected) if unindent else indent_lines(selected, self.INDENT)
        cursor.insertText(replacement)
