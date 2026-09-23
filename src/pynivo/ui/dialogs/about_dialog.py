"""Application identity and installed license information."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QPlainTextEdit, QPushButton, QTabWidget, QVBoxLayout

from pynivo import __version__
from pynivo.paths import application_root, resource_path


def installed_notice(filename: str) -> str:
    path = application_root() / filename
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return f"{filename} is available in the PyNivo source repository."


class AboutDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("About PyNivo")
        self.resize(680, 560)

        icon = QLabel(self)
        pixmap = QPixmap(str(resource_path("resources/branding/pynivo-icon.png")))
        icon.setPixmap(pixmap.scaledToWidth(88))
        icon.setAccessibleName("PyNivo application icon")
        title = QLabel(f"PYNIVO  //  VERSION {__version__}", self)
        title.setObjectName("dialogTitle")
        summary = QLabel(
            "Python, ready when you are.\n\n"
            "A beginner-focused, offline-first Python desktop IDE.\n"
            "Copyright 2026 Asad Abbas. Licensed under Apache License 2.0.",
            self,
        )
        summary.setWordWrap(True)

        tabs = QTabWidget(self)
        tabs.addTab(self._notice_view("LICENSE_NOTICE.txt"), "PyNivo License")
        tabs.addTab(self._notice_view("THIRD_PARTY_NOTICES.md"), "Third-party Notices")
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(summary)
        layout.addWidget(tabs, 1)
        layout.addWidget(close_button)

    def _notice_view(self, filename: str) -> QPlainTextEdit:
        view = QPlainTextEdit(self)
        view.setPlainText(installed_notice(filename))
        view.setReadOnly(True)
        return view
