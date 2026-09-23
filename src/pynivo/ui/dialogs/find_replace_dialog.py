"""Modeless find and replace controls for the active editor."""

from PySide6.QtGui import QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from pynivo.ui.editor import DocumentEditor


class FindReplaceDialog(QDialog):
    def __init__(self, editor: DocumentEditor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Find / Replace")
        self.setModal(False)
        self.setMinimumWidth(460)

        self.find_input = QLineEdit(self)
        self.find_input.setPlaceholderText("Text to find")
        self.find_input.returnPressed.connect(self.find_next)
        self.replace_input = QLineEdit(self)
        self.replace_input.setPlaceholderText("Replacement text")
        self.case_sensitive = QCheckBox("Match case", self)
        self.status = QLabel("", self)
        self.status.setObjectName("sectionTitle")

        find_button = QPushButton("Find Next", self)
        find_button.setObjectName("primaryButton")
        find_button.clicked.connect(self.find_next)
        replace_button = QPushButton("Replace", self)
        replace_button.clicked.connect(self.replace_current)
        replace_all_button = QPushButton("Replace All", self)
        replace_all_button.clicked.connect(self.replace_all)
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)

        layout = QGridLayout(self)
        layout.addWidget(QLabel("Find"), 0, 0)
        layout.addWidget(self.find_input, 0, 1, 1, 3)
        layout.addWidget(QLabel("Replace"), 1, 0)
        layout.addWidget(self.replace_input, 1, 1, 1, 3)
        layout.addWidget(self.case_sensitive, 2, 1)
        layout.addWidget(self.status, 2, 2, 1, 2)
        layout.addWidget(find_button, 3, 0)
        layout.addWidget(replace_button, 3, 1)
        layout.addWidget(replace_all_button, 3, 2)
        layout.addWidget(close_button, 3, 3)

    def set_editor(self, editor: DocumentEditor) -> None:
        self.editor = editor
        self.status.clear()

    def _flags(self) -> QTextDocument.FindFlag:
        if self.case_sensitive.isChecked():
            return QTextDocument.FindFlag.FindCaseSensitively
        return QTextDocument.FindFlag(0)

    def find_next(self) -> bool:
        query = self.find_input.text()
        if not query:
            self.status.setText("Enter text to find")
            return False
        if not self.editor.find(query, self._flags()):
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            if not self.editor.find(query, self._flags()):
                self.status.setText("No matches")
                return False
        self.status.setText("Match found")
        self.editor.ensureCursorVisible()
        return True

    def replace_current(self) -> None:
        cursor = self.editor.textCursor()
        query = self.find_input.text()
        selected = cursor.selectedText()
        if self.case_sensitive.isChecked():
            matches = selected == query
        else:
            matches = selected.casefold() == query.casefold()
        if query and matches:
            cursor.insertText(self.replace_input.text())
        self.find_next()

    def replace_all(self) -> None:
        query = self.find_input.text()
        if not query:
            self.status.setText("Enter text to find")
            return
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        count = 0
        while True:
            cursor = self.editor.document().find(query, cursor, self._flags())
            if cursor.isNull():
                break
            cursor.insertText(self.replace_input.text())
            count += 1
        cursor.endEditBlock()
        suffix = "es" if count != 1 else ""
        self.status.setText(f"Replaced {count} match{suffix}")
