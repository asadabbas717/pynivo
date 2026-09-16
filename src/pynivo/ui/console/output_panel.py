"""Beginner-friendly output panel; intentionally not a full terminal."""

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class OutputPanel(QFrame):
    input_submitted = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("consoleFrame")
        self.output_text_color = "#B9F6E5"
        self.error_text_color = "#FF6B81"
        self._entries: list[tuple[str, bool]] = []
        self.output = QPlainTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Program output appears here.")
        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Type input here, then press Enter")
        self.input.setEnabled(False)
        self.input.returnPressed.connect(self._submit_input)
        clear_button = QPushButton("Clear", self)
        clear_button.clicked.connect(self.clear_output)
        input_row = QHBoxLayout()
        input_row.addWidget(self.input, 1)
        input_row.addWidget(clear_button)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(self.output, 1)
        layout.addLayout(input_row)

    def append_output(self, text: str, *, error: bool = False) -> None:
        self._entries.append((text, error))
        self._append_formatted(text, error)

    def _append_formatted(self, text: str, error: bool) -> None:
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        text_format = QTextCharFormat()
        text_format.setForeground(
            QColor(self.error_text_color if error else self.output_text_color)
        )
        cursor.insertText(text, text_format)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def set_running(self, running: bool) -> None:
        self.input.setEnabled(running)
        if running:
            self.input.setFocus()
        else:
            self.input.clear()

    def _submit_input(self) -> None:
        text = self.input.text()
        self.input.clear()
        self.append_output(f"{text}\n")
        self.input_submitted.emit(text)

    def set_theme(self, theme) -> None:
        self.output_text_color = theme.output_text
        self.error_text_color = theme.error_text
        self.output.clear()
        for text, error in self._entries:
            self._append_formatted(text, error)

    def clear_output(self) -> None:
        self._entries.clear()
        self.output.clear()
