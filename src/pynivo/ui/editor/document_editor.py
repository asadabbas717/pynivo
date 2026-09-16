"""Code editor paired with its file identity and dirty state."""

from pathlib import Path

from PySide6.QtCore import Signal

from pynivo.ui.editor.code_editor import CodeEditor


class DocumentEditor(CodeEditor):
    title_changed = Signal()

    def __init__(self, path: Path | None = None, text: str = "") -> None:
        super().__init__()
        self.path = path
        self.setPlainText(text)
        self.document().setModified(False)
        self.document().modificationChanged.connect(lambda _modified: self.title_changed.emit())

    @property
    def display_name(self) -> str:
        return self.path.name if self.path else "Untitled.py"

    @property
    def tab_title(self) -> str:
        return f"{self.display_name}{' •' if self.document().isModified() else ''}"

    def mark_saved(self, path: Path) -> None:
        self.path = path
        self.document().setModified(False)
        self.title_changed.emit()
