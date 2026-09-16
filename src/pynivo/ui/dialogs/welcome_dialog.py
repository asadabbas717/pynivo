"""Small first-run welcome experience."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout


class WelcomeDialog(QDialog):
    create_requested = Signal()
    open_requested = Signal()
    examples_requested = Signal()
    learning_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to PyNivo")
        self.setModal(False)
        title = QLabel("Welcome to PyNivo")
        title.setStyleSheet("font-size: 26px; font-weight: 600;")
        tagline = QLabel("Python, ready when you are.\nStart coding without setup.")
        tagline.setStyleSheet("font-size: 15px;")
        create = QPushButton("Create Python File")
        learn = QPushButton("Start Learning Python")
        examples = QPushButton("Explore Examples")
        open_file = QPushButton("Open File")
        create.clicked.connect(self.create_requested)
        learn.clicked.connect(self.learning_requested)
        examples.clicked.connect(self.examples_requested)
        open_file.clicked.connect(self.open_requested)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(tagline)
        layout.addSpacing(12)
        layout.addWidget(create)
        layout.addWidget(learn)
        layout.addWidget(examples)
        layout.addWidget(open_file)
