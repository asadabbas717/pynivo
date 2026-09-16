"""Offline lesson browser with runnable starter code."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from pynivo.learning import Lesson, LessonLibrary


class LessonsDialog(QDialog):
    lesson_selected = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Learn Python")
        self.resize(720, 600)
        self.lessons = LessonLibrary().load()
        self.lesson_list = QListWidget()
        for lesson in self.lessons:
            item = QListWidgetItem(f"{lesson.order}. {lesson.title}")
            item.setData(256, lesson)
            self.lesson_list.addItem(item)
        self.explanation = QLabel()
        self.explanation.setWordWrap(True)
        self.code = QPlainTextEdit()
        self.code.setReadOnly(True)
        self.challenge = QLabel()
        self.challenge.setWordWrap(True)
        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.hint.hide()
        hint_button = QPushButton("Show Hint")
        hint_button.clicked.connect(self.hint.show)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Open | QDialogButtonBox.StandardButton.Close
        )
        buttons.button(QDialogButtonBox.StandardButton.Open).setText("Try in Editor")
        buttons.accepted.connect(self._open)
        buttons.rejected.connect(self.reject)
        self.lesson_list.currentItemChanged.connect(self._update)
        layout = QVBoxLayout(self)
        layout.addWidget(self.lesson_list)
        layout.addWidget(self.explanation)
        layout.addWidget(self.code, 1)
        layout.addWidget(self.challenge)
        layout.addWidget(hint_button)
        layout.addWidget(self.hint)
        layout.addWidget(buttons)
        self.lesson_list.setCurrentRow(0)

    def _current(self) -> Lesson | None:
        item = self.lesson_list.currentItem()
        return item.data(256) if item else None

    def _update(self) -> None:
        lesson = self._current()
        if lesson:
            self.explanation.setText(lesson.explanation)
            self.code.setPlainText(lesson.code)
            self.challenge.setText(f"Challenge: {lesson.challenge}")
            self.hint.setText(f"Hint: {lesson.hint}")
            self.hint.hide()

    def _open(self) -> None:
        lesson = self._current()
        if lesson:
            self.lesson_selected.emit(lesson)
            self.accept()
