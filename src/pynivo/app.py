"""PyNivo application startup."""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QStandardPaths, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from pynivo import __version__
from pynivo.paths import resource_path
from pynivo.ui.main_window import MainWindow


def configure_logging() -> Path:
    """Configure bounded application logging and return the log file path."""
    location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
    log_directory = Path(location) / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    log_path = log_directory / "pynivo.log"

    handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    return log_path


def main() -> int:
    """Create and run the Qt application."""
    application = QApplication(sys.argv)
    application.setApplicationName("PyNivo")
    application.setApplicationVersion(__version__)
    application.setOrganizationName("PyNivo")
    application.setWindowIcon(QIcon(str(resource_path("resources/branding/pynivo.ico"))))
    log_path = configure_logging()
    logging.getLogger(__name__).info("PyNivo %s starting; log: %s", __version__, log_path)

    smoke_test = "--smoke-test" in sys.argv
    window = MainWindow(onboarding_enabled=not smoke_test)
    window.show()
    if smoke_test:
        QTimer.singleShot(750, application.quit)
    return application.exec()
