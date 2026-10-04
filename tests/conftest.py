"""Keep one GUI-capable Qt application alive for all component/process tests."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

_APPLICATION = QApplication.instance() or QApplication([])
