"""Main PyNivo window and document workflow."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QTabWidget, QToolBar

from pynivo.core.files import DocumentError, DocumentService
from pynivo.ui.editor import DocumentEditor

LOGGER = logging.getLogger(__name__)
PYTHON_FILTER = "Python files (*.py);;All files (*)"
WELCOME_CODE = """name = input("What's your name? ")
print(f"Hello, {name}!")
"""


class MainWindow(QMainWindow):
    """Beginner-focused workspace coordinating multiple source documents."""

    def __init__(self, document_service: DocumentService | None = None) -> None:
        super().__init__()
        self.documents = document_service or DocumentService()
        self.settings = QSettings()
        self.setWindowTitle("PyNivo — Python, ready when you are.")
        self.resize(1100, 720)
        self.setMinimumSize(760, 500)
        self._build_actions()
        self._build_menu()
        self._build_toolbar()
        self._build_workspace()
        self._restore_settings()
        self.new_document(WELCOME_CODE)

    def _build_actions(self) -> None:
        self.new_action = self._action("New", QKeySequence.StandardKey.New, self.new_document)
        self.open_action = self._action(
            "Open…", QKeySequence.StandardKey.Open, self.open_document_dialog
        )
        self.save_action = self._action(
            "Save", QKeySequence.StandardKey.Save, self.save_current_document
        )
        self.save_as_action = self._action(
            "Save As…", QKeySequence.StandardKey.SaveAs, self.save_current_document_as
        )
        self.close_action = self._action(
            "Close File", QKeySequence.StandardKey.Close, self.close_current_tab
        )
        self.exit_action = self._action("Exit", QKeySequence.StandardKey.Quit, self.close)
        self.run_action = self._action("▶ Run", QKeySequence("F5"), lambda: None)
        self.run_action.setEnabled(False)
        self.run_action.setToolTip("Run support arrives in the next milestone")
        self.stop_action = self._action("■ Stop", QKeySequence("Shift+F5"), lambda: None)
        self.stop_action.setEnabled(False)
        self.font_up_action = self._action(
            "Increase Editor Font", QKeySequence("Ctrl++"), lambda: self.change_font_size(1)
        )
        self.font_down_action = self._action(
            "Decrease Editor Font", QKeySequence("Ctrl+-"), lambda: self.change_font_size(-1)
        )

    def _action(self, label, shortcut, callback) -> QAction:
        action = QAction(label, self)
        action.setShortcut(shortcut)
        action.triggered.connect(callback)
        return action

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addActions(
            [
                self.new_action,
                self.open_action,
                self.save_action,
                self.save_as_action,
                self.close_action,
            ]
        )
        self.recent_menu = file_menu.addMenu("Open Recent")
        self.refresh_recent_menu()
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = self.menuBar().addMenu("&Edit")
        for label, shortcut, method in (
            ("Undo", QKeySequence.StandardKey.Undo, "undo"),
            ("Redo", QKeySequence.StandardKey.Redo, "redo"),
            ("Cut", QKeySequence.StandardKey.Cut, "cut"),
            ("Copy", QKeySequence.StandardKey.Copy, "copy"),
            ("Paste", QKeySequence.StandardKey.Paste, "paste"),
            ("Select All", QKeySequence.StandardKey.SelectAll, "selectAll"),
        ):
            edit_menu.addAction(
                self._action(label, shortcut, lambda checked=False, name=method: self._edit(name))
            )
        view_menu = self.menuBar().addMenu("&View")
        view_menu.addActions([self.font_up_action, self.font_down_action])

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main toolbar", self)
        toolbar.setObjectName("main_toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.addActions([self.new_action, self.open_action, self.save_action])
        toolbar.addSeparator()
        toolbar.addActions([self.run_action, self.stop_action])
        self.addToolBar(toolbar)

    def _build_workspace(self) -> None:
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setCentralWidget(self.tabs)

    def new_document(self, text: str = "") -> DocumentEditor:
        editor = DocumentEditor(text=text if isinstance(text, str) else "")
        self.prepare_editor(editor)
        editor.setFocus()
        return editor

    def prepare_editor(self, editor: DocumentEditor) -> None:
        font = editor.font()
        font.setPointSize(self.font_size())
        editor.setFont(font)
        editor.title_changed.connect(lambda: self.update_editor_title(editor))
        self.tabs.setCurrentIndex(self.tabs.addTab(editor, editor.tab_title))

    def open_document_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Open Python File", "", PYTHON_FILTER)
        if filename:
            self.open_document(Path(filename))

    def open_document(self, path: Path) -> bool:
        resolved = path.expanduser().resolve()
        for index in range(self.tabs.count()):
            if self.editor_at(index).path == resolved:
                self.tabs.setCurrentIndex(index)
                return True
        try:
            document = self.documents.load(resolved)
        except DocumentError as error:
            self.show_file_error("Could not open file", error)
            return False
        self.prepare_editor(DocumentEditor(document.path, document.text))
        self.remember_recent(document.path)
        self.statusBar().showMessage(f"Opened {document.path.name}", 3000)
        return True

    def save_current_document(self) -> bool:
        editor = self.current_editor()
        return (
            self.save_current_document_as()
            if editor.path is None
            else self.save_editor(editor, editor.path)
        )

    def save_current_document_as(self) -> bool:
        editor = self.current_editor()
        suggestion = str(editor.path or Path.cwd() / editor.display_name)
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Python File", suggestion, PYTHON_FILTER
        )
        return bool(filename) and self.save_editor(editor, Path(filename))

    def save_editor(self, editor: DocumentEditor, path: Path) -> bool:
        try:
            document = self.documents.save(path, editor.toPlainText())
        except DocumentError as error:
            self.show_file_error("Could not save file", error)
            return False
        editor.mark_saved(document.path)
        self.remember_recent(document.path)
        self.statusBar().showMessage(f"Saved {document.path.name}", 3000)
        return True

    def close_current_tab(self) -> bool:
        return self.close_tab(self.tabs.currentIndex())

    def close_tab(self, index: int) -> bool:
        if index < 0:
            return True
        editor = self.editor_at(index)
        if not self.confirm_close(editor):
            return False
        self.tabs.removeTab(index)
        editor.deleteLater()
        if not self.tabs.count():
            self.new_document()
        return True

    def confirm_close(self, editor: DocumentEditor) -> bool:
        if not editor.document().isModified():
            return True
        answer = QMessageBox.warning(
            self,
            "Unsaved changes",
            f"Save changes to {editor.display_name}?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            return False
        if answer == QMessageBox.StandardButton.Save:
            self.tabs.setCurrentWidget(editor)
            return self.save_current_document()
        return True

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        for index in range(self.tabs.count()):
            if not self.confirm_close(self.editor_at(index)):
                event.ignore()
                return
        self.settings.setValue("window/geometry", self.saveGeometry())
        event.accept()

    def current_editor(self) -> DocumentEditor:
        return self.editor_at(self.tabs.currentIndex())

    def editor_at(self, index: int) -> DocumentEditor:
        editor = self.tabs.widget(index)
        if not isinstance(editor, DocumentEditor):
            raise RuntimeError("No source editor is available")
        return editor

    def update_editor_title(self, editor: DocumentEditor) -> None:
        index = self.tabs.indexOf(editor)
        if index >= 0:
            self.tabs.setTabText(index, editor.tab_title)
        self.current_tab_changed(self.tabs.currentIndex())

    def current_tab_changed(self, index: int) -> None:
        if index >= 0:
            editor = self.editor_at(index)
            self.setWindowTitle(f"{editor.tab_title} — PyNivo")

    def _edit(self, method: str) -> None:
        getattr(self.current_editor(), method)()

    def font_size(self) -> int:
        return max(8, min(28, self.settings.value("editor/font_size", 11, int)))

    def change_font_size(self, delta: int) -> None:
        size = max(8, min(28, self.current_editor().font().pointSize() + delta))
        self.settings.setValue("editor/font_size", size)
        for index in range(self.tabs.count()):
            editor = self.editor_at(index)
            font = editor.font()
            font.setPointSize(size)
            editor.setFont(font)
        self.statusBar().showMessage(f"Editor font: {size} pt", 2000)

    def _restore_settings(self) -> None:
        geometry = self.settings.value("window/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

    def recent_paths(self) -> list[Path]:
        values = self.settings.value("files/recent", [], list)
        return [Path(value) for value in values if Path(value).is_file()][:10]

    def remember_recent(self, path: Path) -> None:
        paths = [candidate for candidate in self.recent_paths() if candidate != path]
        self.settings.setValue("files/recent", [str(item) for item in [path, *paths][:10]])
        self.refresh_recent_menu()

    def refresh_recent_menu(self) -> None:
        self.recent_menu.clear()
        paths = self.recent_paths()
        self.recent_menu.setEnabled(bool(paths))
        for path in paths:
            action = self.recent_menu.addAction(path.name)
            action.setToolTip(str(path))
            action.triggered.connect(lambda checked=False, item=path: self.open_document(item))

    def show_file_error(self, title: str, error: DocumentError) -> None:
        LOGGER.warning("%s: %s", title, error)
        QMessageBox.critical(self, title, str(error))
