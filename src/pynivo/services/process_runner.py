"""Asynchronous learner-program execution backed by QProcess."""

from __future__ import annotations

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, QTimer, Signal

from pynivo.core.execution import ExecutionRequest


class ProcessRunner(QObject):
    """Run exactly one learner program outside the GUI process."""

    output_received = Signal(str)
    error_received = Signal(str)
    started = Signal()
    finished = Signal(int, bool)
    launch_failed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.process.started.connect(self.started)
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.finished.connect(self._finished)
        self.process.errorOccurred.connect(self._process_error)
        self._stopping = False

    @property
    def is_running(self) -> bool:
        return self.process.state() != QProcess.ProcessState.NotRunning

    def run(self, request: ExecutionRequest) -> bool:
        if self.is_running:
            return False
        self._stopping = False
        self.process.setWorkingDirectory(str(request.working_directory))
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert("PYTHONIOENCODING", "utf-8")
        environment.insert("PYTHONUTF8", "1")
        self.process.setProcessEnvironment(environment)
        self.process.setProgram(str(request.executable))
        self.process.setArguments(list(request.arguments))
        self.process.start()
        return True

    def write_input(self, text: str) -> bool:
        if not self.is_running:
            return False
        self.process.write((text + "\n").encode("utf-8"))
        return True

    def stop(self) -> bool:
        if not self.is_running:
            return False
        self._stopping = True
        self.process.terminate()
        QTimer.singleShot(2000, self._kill_if_running)
        return True

    def _kill_if_running(self) -> None:
        if self.is_running:
            self.process.kill()

    def _read_stdout(self) -> None:
        text = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if text:
            self.output_received.emit(text)

    def _read_stderr(self) -> None:
        text = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace")
        if text:
            self.error_received.emit(text)

    def _finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        self._read_stdout()
        self._read_stderr()
        stopped = self._stopping
        self._stopping = False
        self.finished.emit(exit_code, stopped)

    def _process_error(self, error: QProcess.ProcessError) -> None:
        if error == QProcess.ProcessError.FailedToStart:
            self.launch_failed.emit(self.process.errorString())
