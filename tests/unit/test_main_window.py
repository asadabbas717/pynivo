import pytest
from PySide6.QtCore import QSettings
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMessageBox

from pynivo.ui.main_window import MainWindow

MAXIMUM_STDERR_CHARACTERS = 250_000


@pytest.fixture
def window(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "pynivo.ui.main_window.QSettings",
        lambda: QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat),
    )
    widget = MainWindow(onboarding_enabled=False, recovery_enabled=False)
    widget.recovery_timer.stop()
    widget.recovery.directory = tmp_path
    widget.recovery.snapshot_path = tmp_path / "session.json"
    yield widget
    widget.deleteLater()


def test_stderr_is_bounded_and_keeps_final_traceback(window):
    window.program_error_output("x" * (MAXIMUM_STDERR_CHARACTERS + 100))
    window.program_error_output("\nValueError: final error\n")
    assert len(window.stderr_buffer) == MAXIMUM_STDERR_CHARACTERS
    assert window.stderr_buffer.endswith("ValueError: final error\n")


@pytest.mark.parametrize(
    "filename,edited,navigates",
    [("main.py", False, True), ("imported.py", False, False), ("main.py", True, False)],
)
def test_navigation_uses_run_file_and_unchanged_source(
    window, tmp_path, filename, edited, navigates
):
    editor = window.current_editor()
    source = "first = 1\nraise ValueError('bad')\n"
    editor.setPlainText(source)
    editor.path = tmp_path / "main.py"
    window.running_document_path = editor.path
    window.running_source_code = source
    other = window.new_document("other")
    if edited:
        editor.setPlainText("changed\n" + source)
    window.stderr_buffer = f'  File "{tmp_path / filename}", line 2\nValueError: bad\n'
    window.program_finished(1, False)
    assert window.current_editor() is (editor if navigates else other)


def test_cancel_save_prevents_execution(window, monkeypatch):
    monkeypatch.setattr(window, "save_current_document", lambda: False)
    monkeypatch.setattr(window.runner, "run", lambda request: pytest.fail("unexpected run"))
    window.run_current_document()
    assert window.running_document_path is None


def test_close_cancel_preserves_dirty_document(window, monkeypatch):
    editor = window.current_editor()
    editor.insertPlainText("private draft")
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: QMessageBox.StandardButton.Cancel)
    assert not window.close_tab(0)
    assert window.current_editor() is editor
    assert "private draft" in editor.toPlainText()


def test_untouched_starter_code_is_recoverable(window):
    editor = window.new_document("print('starter')")
    assert editor.document().isModified()
    window.snapshot_recovery()
    assert any(item.text == "print('starter')" for item in window.recovery.load())


def test_malformed_traceback_filename_cannot_break_completion(window, tmp_path):
    window.running_document_path = tmp_path / "main.py"
    assert not window._error_filename_matches_run("bad\x00.py")
    assert window._error_filename_matches_run("main.py")


def test_cancel_window_close_does_not_stop_program(window, monkeypatch):
    stops = []
    monkeypatch.setattr(type(window.runner), "is_running", property(lambda self: True))
    monkeypatch.setattr(window.runner, "stop", lambda: stops.append(True))
    monkeypatch.setattr(window, "confirm_close", lambda editor: False)
    event = QCloseEvent()
    window.closeEvent(event)
    assert not event.isAccepted()
    assert not stops


def test_recovery_cleanup_failure_does_not_abort_accepted_close(window, monkeypatch, caplog):
    monkeypatch.setattr(window, "confirm_close", lambda editor: True)

    def fail_clear():
        raise PermissionError("snapshot locked")

    monkeypatch.setattr(window.recovery, "clear", fail_clear)
    event = QCloseEvent()
    window.closeEvent(event)
    assert event.isAccepted()
    assert "Could not clear recovery snapshot" in caplog.text
