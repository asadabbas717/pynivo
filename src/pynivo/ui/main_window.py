"""Main application window shell."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Beginner-focused shell for the PyNivo workspace."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PyNivo — Python, ready when you are.")
        self.resize(1100, 720)
        self.setMinimumSize(760, 500)
        self._build_toolbar()
        self._build_welcome_view()
        self.statusBar().showMessage("Ready")

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main toolbar", self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        actions = (
            ("New", QKeySequence.StandardKey.New, "Create a new Python file"),
            ("Open", QKeySequence.StandardKey.Open, "Open a Python file"),
            ("Save", QKeySequence.StandardKey.Save, "Save the current Python file"),
        )
        for text, shortcut, tooltip in actions:
            action = QAction(text, self)
            action.setShortcut(shortcut)
            action.setToolTip(tooltip)
            action.setEnabled(False)
            toolbar.addAction(action)

        toolbar.addSeparator()
        run_action = QAction("▶ Run", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.setToolTip("Run the current Python file (coming in the execution milestone)")
        run_action.setEnabled(False)
        toolbar.addAction(run_action)

        stop_action = QAction("■ Stop", self)
        stop_action.setShortcut(QKeySequence("Shift+F5"))
        stop_action.setToolTip("Stop the running program")
        stop_action.setEnabled(False)
        toolbar.addAction(stop_action)

    def _build_welcome_view(self) -> None:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(72, 72, 72, 72)
        layout.setSpacing(18)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Welcome to PyNivo")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: 600;")

        tagline = QLabel("Start coding Python without setup.")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("font-size: 17px; color: palette(mid);")

        next_step = QLabel(
            "The application foundation is ready. The editor and Run experience "
            "are the next milestone."
        )
        next_step.setAlignment(Qt.AlignmentFlag.AlignCenter)
        next_step.setWordWrap(True)
        next_step.setMaximumWidth(560)

        start_button = QPushButton("Start Learning Python")
        start_button.setEnabled(False)
        start_button.setToolTip("Available in a future learning milestone")
        start_button.setMinimumHeight(42)
        start_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(tagline)
        layout.addWidget(next_step)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.setCentralWidget(container)
