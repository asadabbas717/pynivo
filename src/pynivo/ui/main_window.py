"""Main PyNivo window and document workflow."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QSettings, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from pynivo import __version__
from pynivo.core.errors import ErrorAnalyzer
from pynivo.core.execution import ExecutionRequest, ExecutionRequestError
from pynivo.core.files import DocumentError, DocumentService, RecoveryDocument, RecoveryService
from pynivo.core.runtime.manager import RuntimeResolver, RuntimeValidationError
from pynivo.paths import application_root
from pynivo.services import ProcessRunner
from pynivo.ui.console import OutputPanel
from pynivo.ui.dialogs import (
    AboutDialog,
    ExamplesDialog,
    FindReplaceDialog,
    LessonsDialog,
    WelcomeDialog,
)
from pynivo.ui.editor import DocumentEditor
from pynivo.ui.onboarding import should_show_welcome
from pynivo.ui.themes import apply_theme

LOGGER = logging.getLogger(__name__)
PYTHON_FILTER = "Python files (*.py);;All files (*)"
WELCOME_CODE = """name = input("What's your name? ")
print(f"Hello, {name}!")
"""


class MainWindow(QMainWindow):
    """Beginner-focused workspace coordinating multiple source documents."""

    def __init__(
        self,
        document_service: DocumentService | None = None,
        *,
        onboarding_enabled: bool = True,
    ) -> None:
        super().__init__()
        self.documents = document_service or DocumentService()
        self.runtime = RuntimeResolver(application_root())
        self.error_analyzer = ErrorAnalyzer()
        self.stderr_buffer = ""
        self.running_document_path: Path | None = None
        self.running_source_code = ""
        self.settings = QSettings()
        recovery_root = (
            Path(
                QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.AppLocalDataLocation
                )
            )
            / "recovery"
        )
        self.recovery = RecoveryService(recovery_root)
        application = QApplication.instance()
        if not isinstance(application, QApplication):
            raise RuntimeError("PyNivo requires a QApplication")
        self.theme = apply_theme(application, self.settings.value("appearance/theme", "dark"))
        self.setWindowTitle("PyNivo — Python, ready when you are.")
        self.resize(1100, 720)
        self.setMinimumSize(760, 500)
        self._build_actions()
        self._build_menu()
        self._build_toolbar()
        self._build_workspace()
        self.runner = ProcessRunner(self)
        self.runner.output_received.connect(self.output_panel.append_output)
        self.runner.error_received.connect(self.program_error_output)
        self.runner.started.connect(self.program_started)
        self.runner.finished.connect(self.program_finished)
        self.runner.launch_failed.connect(self.program_launch_failed)
        self.output_panel.input_submitted.connect(self.runner.write_input)
        self._restore_settings()
        if not self.restore_recovery_session():
            self.new_document(WELCOME_CODE)
        self.recovery_timer = QTimer(self)
        self.recovery_timer.setInterval(15_000)
        self.recovery_timer.timeout.connect(self.snapshot_recovery)
        self.recovery_timer.start()
        seen_version = self.settings.value("welcome/seen_version", None)
        if should_show_welcome(
            seen_version,
            __version__,
            onboarding_enabled=onboarding_enabled,
        ):
            QTimer.singleShot(0, self.show_welcome)

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
        self.run_action = self._action("▶ Run", QKeySequence("F5"), self.run_current_document)
        self.run_action.setToolTip("Run the current Python file")
        self.stop_action = self._action("■ Stop", QKeySequence("Shift+F5"), self.stop_program)
        self.stop_action.setEnabled(False)
        self.font_up_action = self._action(
            "Increase Editor Font", QKeySequence("Ctrl++"), lambda: self.change_font_size(1)
        )
        self.font_down_action = self._action(
            "Decrease Editor Font", QKeySequence("Ctrl+-"), lambda: self.change_font_size(-1)
        )
        self.find_action = self._action(
            "Find / Replace", QKeySequence.StandardKey.Find, self.show_find
        )
        self.examples_action = self._action("Examples", QKeySequence("Ctrl+E"), self.show_examples)
        self.lessons_action = self._action(
            "Start Learning", QKeySequence("Ctrl+L"), self.show_lessons
        )
        self.welcome_action = self._action("Welcome", QKeySequence(), self.show_welcome)
        self.about_action = self._action("About PyNivo", QKeySequence(), self.show_about)
        self.theme_action = self._action(
            "Switch to Light", QKeySequence("Ctrl+Shift+T"), self.toggle_theme
        )
        if self.theme.name == "light":
            self.theme_action.setText("Switch to Dark")

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
        edit_menu.addAction(self.find_action)
        edit_menu.addSeparator()
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
        view_menu.addActions([self.font_up_action, self.font_down_action, self.theme_action])
        learn_menu = self.menuBar().addMenu("&Learn")
        learn_menu.addActions([self.lessons_action, self.examples_action, self.welcome_action])
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self.about_action)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main toolbar", self)
        toolbar.setObjectName("main_toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.addActions([self.new_action, self.open_action, self.save_action])
        toolbar.addSeparator()
        toolbar.addActions([self.run_action, self.stop_action])
        run_button = toolbar.widgetForAction(self.run_action)
        if run_button:
            run_button.setObjectName("primaryButton")
        toolbar.addSeparator()
        toolbar.addActions([self.lessons_action, self.examples_action])
        self.addToolBar(toolbar)

    def _build_workspace(self) -> None:
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.output_panel = OutputPanel(self)
        self.output_panel.set_theme(self.theme)
        splitter = QSplitter(Qt.Orientation.Vertical, self)
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.output_panel)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([540, 180])
        rail = QFrame(self)
        rail.setObjectName("sideRail")
        rail.setFixedWidth(190)
        rail_layout = QVBoxLayout(rail)
        rail_layout.setContentsMargins(18, 22, 18, 18)
        brand = QLabel("PYNIVO")
        brand.setObjectName("brand")
        tagline = QLabel("PYTHON // READY")
        tagline.setObjectName("sectionTitle")
        rail_layout.addWidget(brand)
        rail_layout.addWidget(tagline)
        rail_layout.addSpacing(28)
        for label, action in (
            ("01  NEW FILE", self.new_action),
            ("02  OPEN FILE", self.open_action),
            ("03  LEARN", self.lessons_action),
            ("04  EXAMPLES", self.examples_action),
        ):
            button = self._rail_button(label, action)
            rail_layout.addWidget(button)
        rail_layout.addStretch()
        mode = QLabel("LOCAL MODE  ●")
        mode.setObjectName("sectionTitle")
        mode.setToolTip("PyNivo works offline. Learner code runs in a child process.")
        rail_layout.addWidget(mode)
        container = QWidget(self)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(rail)
        layout.addWidget(splitter, 1)
        self.setCentralWidget(container)

    def _rail_button(self, label: str, action: QAction) -> QPushButton:
        button = QPushButton(label)
        button.setMinimumHeight(40)
        button.clicked.connect(action.trigger)
        return button

    def new_document(self, text: str = "") -> DocumentEditor:
        editor = DocumentEditor(text=text if isinstance(text, str) else "")
        self.prepare_editor(editor)
        editor.setFocus()
        return editor

    def prepare_editor(self, editor: DocumentEditor) -> None:
        font = editor.font()
        font.setPointSize(self.font_size())
        editor.setFont(font)
        editor.set_theme(self.theme)
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
        if self.runner.is_running:
            self.runner.stop()
        for index in range(self.tabs.count()):
            if not self.confirm_close(self.editor_at(index)):
                event.ignore()
                return
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.recovery.clear()
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
            if hasattr(self, "find_dialog"):
                self.find_dialog.set_editor(editor)

    def show_find(self) -> None:
        if not hasattr(self, "find_dialog"):
            self.find_dialog = FindReplaceDialog(self.current_editor(), self)
        else:
            self.find_dialog.set_editor(self.current_editor())
        selected = self.current_editor().textCursor().selectedText()
        if selected and "\u2029" not in selected:
            self.find_dialog.find_input.setText(selected)
        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.activateWindow()
        self.find_dialog.find_input.setFocus()
        self.find_dialog.find_input.selectAll()

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

    def toggle_theme(self) -> None:
        name = "light" if self.theme.name == "dark" else "dark"
        application = QApplication.instance()
        if isinstance(application, QApplication):
            self.theme = apply_theme(application, name)
        self.settings.setValue("appearance/theme", name)
        self.theme_action.setText("Switch to Dark" if name == "light" else "Switch to Light")
        self.output_panel.set_theme(self.theme)
        for index in range(self.tabs.count()):
            self.editor_at(index).set_theme(self.theme)

    def _restore_settings(self) -> None:
        geometry = self.settings.value("window/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

    def snapshot_recovery(self) -> None:
        documents = tuple(
            RecoveryDocument(
                path=str(editor.path) if editor.path else None,
                text=editor.toPlainText(),
            )
            for index in range(self.tabs.count())
            if (editor := self.editor_at(index)).document().isModified()
        )
        try:
            self.recovery.save(documents)
        except OSError as error:
            LOGGER.warning("Could not update recovery snapshot: %s", error)

    def restore_recovery_session(self) -> bool:
        documents = self.recovery.load()
        if not documents:
            return False
        answer = QMessageBox.question(
            self,
            "Recover unsaved work",
            f"PyNivo found {len(documents)} unsaved document(s) from an earlier session. "
            "Recover them?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.No:
            self.recovery.clear()
            return False
        for document in documents:
            path = Path(document.path) if document.path else None
            editor = DocumentEditor(path=path, text=document.text)
            self.prepare_editor(editor)
            editor.document().setModified(True)
        self.statusBar().showMessage("Recovered unsaved work", 5000)
        return True

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

    def show_examples(self) -> None:
        dialog = ExamplesDialog(self)
        dialog.example_selected.connect(lambda example: self.new_document(example.code))
        dialog.exec()

    def show_lessons(self) -> None:
        dialog = LessonsDialog(self)
        dialog.lesson_selected.connect(lambda lesson: self.new_document(lesson.code))
        dialog.exec()

    def show_welcome(self) -> None:
        self.settings.setValue("welcome/seen_version", __version__)
        dialog = WelcomeDialog(self)
        dialog.create_requested.connect(lambda: (self.new_document(), dialog.accept()))
        dialog.open_requested.connect(lambda: (dialog.accept(), self.open_document_dialog()))
        dialog.examples_requested.connect(lambda: (dialog.accept(), self.show_examples()))
        dialog.learning_requested.connect(lambda: (dialog.accept(), self.show_lessons()))
        dialog.show()
        self.welcome_dialog = dialog

    def show_about(self) -> None:
        AboutDialog(self).exec()

    def run_current_document(self) -> None:
        if self.runner.is_running:
            return
        editor = self.current_editor()
        if (
            editor.path is None or editor.document().isModified()
        ) and not self.save_current_document():
            return
        executable = self.runtime.locate_runtime()
        if executable is None:
            QMessageBox.critical(
                self, "Python runtime unavailable", "PyNivo could not find Python."
            )
            return
        try:
            runtime = self.runtime.validate_runtime(executable)
            request = ExecutionRequest.for_script(runtime.executable, editor.path)
        except (RuntimeValidationError, ExecutionRequestError) as error:
            QMessageBox.critical(self, "Could not run program", str(error))
            return
        self.output_panel.clear_output()
        self.stderr_buffer = ""
        self.running_document_path = editor.path
        self.running_source_code = editor.toPlainText()
        self.output_panel.append_output(f"Running {editor.path.name}…\n")
        if not self.runner.run(request):
            self._clear_running_document()
            self.output_panel.append_output("A program is already running.\n", error=True)

    def stop_program(self) -> None:
        if self.runner.stop():
            self.statusBar().showMessage("Stopping program…")

    def program_started(self) -> None:
        self.run_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.output_panel.set_running(True)
        self.statusBar().showMessage("Program running")

    def program_finished(self, exit_code: int, stopped: bool) -> None:
        self.run_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.output_panel.set_running(False)
        if stopped:
            message = "Program stopped."
        elif exit_code == 0:
            message = "Program finished successfully."
        else:
            message = f"Program finished with exit code {exit_code}."
            error = self.error_analyzer.analyze(self.stderr_buffer, self.running_source_code)
            if error:
                self.output_panel.append_output(
                    self.error_analyzer.format_beginner_message(error), error=True
                )
                editor = self._running_editor()
                if editor is not None and error.line_number:
                    cursor = QTextCursor(
                        editor.document().findBlockByLineNumber(error.line_number - 1)
                    )
                    self.tabs.setCurrentWidget(editor)
                    editor.setTextCursor(cursor)
                    editor.centerCursor()
                    editor.setFocus()
        self.output_panel.append_output(f"\n{message}\n", error=exit_code != 0 and not stopped)
        self.statusBar().showMessage(message, 5000)
        self._clear_running_document()

    def program_error_output(self, text: str) -> None:
        self.stderr_buffer += text
        self.output_panel.append_output(text, error=True)

    def program_launch_failed(self, message: str) -> None:
        self.run_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.output_panel.set_running(False)
        self.output_panel.append_output(f"Could not start Python: {message}\n", error=True)
        self._clear_running_document()

    def _running_editor(self) -> DocumentEditor | None:
        if self.running_document_path is None:
            return None
        for index in range(self.tabs.count()):
            editor = self.editor_at(index)
            if editor.path == self.running_document_path:
                return editor
        return None

    def _clear_running_document(self) -> None:
        self.running_document_path = None
        self.running_source_code = ""
