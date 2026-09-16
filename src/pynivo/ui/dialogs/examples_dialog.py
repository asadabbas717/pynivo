"""Browse bundled examples without requiring a network connection."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QVBoxLayout,
)

from pynivo.learning import Example, ExampleLibrary


class ExamplesDialog(QDialog):
    example_selected = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Python Examples")
        self.resize(680, 520)
        self.examples = ExampleLibrary().load()
        self.list_widget = QListWidget(self)
        for example in self.examples:
            item = QListWidgetItem(f"{example.category}  ·  {example.title}")
            item.setData(256, example)
            self.list_widget.addItem(item)
        self.description = QLabel()
        self.description.setWordWrap(True)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Open | QDialogButtonBox.StandardButton.Close
        )
        buttons.button(QDialogButtonBox.StandardButton.Open).setText("Open in Editor")
        buttons.accepted.connect(self._open)
        buttons.rejected.connect(self.reject)
        self.list_widget.currentItemChanged.connect(self._update_preview)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose an example to explore and change:"))
        layout.addWidget(self.list_widget)
        layout.addWidget(self.description)
        layout.addWidget(self.preview, 1)
        layout.addWidget(buttons)
        if self.examples:
            self.list_widget.setCurrentRow(0)

    def _current(self) -> Example | None:
        item = self.list_widget.currentItem()
        return item.data(256) if item else None

    def _update_preview(self) -> None:
        example = self._current()
        if example:
            self.description.setText(example.description)
            self.preview.setPlainText(example.code)

    def _open(self) -> None:
        example = self._current()
        if example:
            self.example_selected.emit(example)
            self.accept()
