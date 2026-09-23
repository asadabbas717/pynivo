"""Offline course browser with persistent progress and editable starter code."""

from dataclasses import replace

from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pynivo.learning import CourseProgress, Lesson, LessonLibrary


class LessonsDialog(QDialog):
    lesson_selected = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PyNivo Learning Path")
        self.resize(900, 650)
        self.settings = QSettings()
        self.lessons = LessonLibrary().load()
        stored = self.settings.value("learning/completed", [], list)
        valid_ids = {lesson.identifier for lesson in self.lessons}
        self.progress = CourseProgress(frozenset(item for item in stored if item in valid_ids))
        self._build_interface()
        self._refresh_lesson_list()
        self.lesson_list.setCurrentRow(0)

    def _build_interface(self) -> None:
        title = QLabel("PYTHON // LEARNING PATH")
        title.setObjectName("dialogTitle")
        self.progress_label = QLabel()
        self.progress_label.setObjectName("sectionTitle")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.lesson_list = QListWidget()
        self.lesson_list.setMinimumWidth(260)
        self.lesson_list.currentItemChanged.connect(self._update_lesson)

        self.lesson_title = QLabel()
        self.lesson_title.setObjectName("dialogTitle")
        self.concepts = QLabel()
        self.concepts.setObjectName("conceptBadge")
        self.explanation = QLabel()
        self.explanation.setWordWrap(True)
        self.code = QPlainTextEdit()
        self.challenge = QLabel()
        self.challenge.setWordWrap(True)
        self.challenge.setObjectName("challengeCard")
        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.hint.setObjectName("hintCard")
        self.hint.hide()

        previous = QPushButton("← Previous")
        previous.clicked.connect(lambda: self._move(-1))
        next_button = QPushButton("Next →")
        next_button.clicked.connect(lambda: self._move(1))
        hint_button = QPushButton("Show Hint")
        hint_button.clicked.connect(self.hint.show)
        reset_button = QPushButton("Reset Code")
        reset_button.clicked.connect(self._reset_code)
        self.complete_button = QPushButton("Mark Complete")
        self.complete_button.clicked.connect(self._mark_complete)
        try_button = QPushButton("Try in Editor")
        try_button.setObjectName("primaryButton")
        try_button.clicked.connect(self._open)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)

        navigation = QHBoxLayout()
        navigation.addWidget(previous)
        navigation.addWidget(next_button)
        navigation.addStretch()
        navigation.addWidget(hint_button)
        navigation.addWidget(reset_button)

        actions = QHBoxLayout()
        actions.addWidget(self.complete_button)
        actions.addStretch()
        actions.addWidget(try_button)
        actions.addWidget(close_button)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.addWidget(self.progress_label)
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.lesson_list, 1)
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.addWidget(self.lesson_title)
        right_layout.addWidget(self.concepts)
        right_layout.addWidget(self.explanation)
        right_layout.addWidget(self.code, 1)
        right_layout.addWidget(self.challenge)
        right_layout.addLayout(navigation)
        right_layout.addWidget(self.hint)
        right_layout.addLayout(actions)
        content = QHBoxLayout()
        content.addWidget(left, 1)
        content.addWidget(right, 2)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.addWidget(title)
        layout.addLayout(content, 1)

    def _refresh_lesson_list(self) -> None:
        selected = self.lesson_list.currentRow()
        self.lesson_list.clear()
        for lesson in self.lessons:
            marker = "✓" if lesson.identifier in self.progress.completed else "○"
            item = QListWidgetItem(f"{marker}  {lesson.order:02}  {lesson.title}")
            item.setData(Qt.ItemDataRole.UserRole, lesson)
            self.lesson_list.addItem(item)
        completed = len(self.progress.completed)
        self.progress_label.setText(f"{completed} of {len(self.lessons)} lessons complete")
        self.progress_bar.setValue(self.progress.percentage(len(self.lessons)))
        if selected >= 0:
            self.lesson_list.setCurrentRow(selected)

    def _current(self) -> Lesson | None:
        item = self.lesson_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _update_lesson(self) -> None:
        lesson = self._current()
        if lesson:
            self.lesson_title.setText(f"{lesson.order:02} // {lesson.title}")
            self.concepts.setText("  ·  ".join(concept.upper() for concept in lesson.concepts))
            self.explanation.setText(lesson.explanation)
            self.code.setPlainText(lesson.code)
            self.challenge.setText(f"CHALLENGE\n{lesson.challenge}")
            self.hint.setText(f"HINT\n{lesson.hint}")
            self.hint.hide()
            done = lesson.identifier in self.progress.completed
            self.complete_button.setText("Completed ✓" if done else "Mark Complete")
            self.complete_button.setEnabled(not done)

    def _move(self, offset: int) -> None:
        row = max(0, min(self.lesson_list.count() - 1, self.lesson_list.currentRow() + offset))
        self.lesson_list.setCurrentRow(row)

    def _reset_code(self) -> None:
        lesson = self._current()
        if lesson:
            self.code.setPlainText(lesson.code)

    def _mark_complete(self) -> None:
        lesson = self._current()
        if lesson:
            row = self.lesson_list.currentRow()
            self.progress = self.progress.mark_complete(lesson.identifier)
            self.settings.setValue("learning/completed", sorted(self.progress.completed))
            self._refresh_lesson_list()
            self.lesson_list.setCurrentRow(row)

    def _open(self) -> None:
        lesson = self._current()
        if lesson:
            self.lesson_selected.emit(replace(lesson, code=self.code.toPlainText()))
            self.accept()
