# Architecture

PyNivo uses a `src` package layout and keeps framework-dependent UI code separate from core
application logic.

## Boundaries

- `pynivo.ui` owns Qt widgets and user interaction.
- `pynivo.ui.themes` centralizes the complete application palette and QSS for persistent light and
  dark modes; editor token and console colors derive from the same theme model.
- `pynivo.core.runtime` locates and validates Python runtimes. The current system-runtime
  implementation supports development, while the resolver prefers a validated private runtime
  stored beside the packaged application.
- `pynivo.core.execution` describes validated child-process launches. A later QProcess service
  will consume these requests and own stdout, stderr, stdin, stopping, and process state.
- `pynivo.core.files` performs UTF-8 document loading and atomic same-folder replacement. It does
  not display dialogs or depend on Qt.
- `pynivo.app` is the composition root. It starts logging, Qt, and the main window.
- `pynivo.services.process_runner` adapts an `ExecutionRequest` to asynchronous `QProcess`
  lifecycle signals. Learner code never enters the GUI process.

Core modules do not import Qt. This keeps validation logic fast to test and prevents UI concerns
from leaking into future runtime, file, error-analysis, and learning services.

## Execution security boundary

Learner programs will run as separate processes and will never be imported into the GUI process.
Arguments are represented structurally and are not concatenated into a shell command. Process
separation improves reliability and responsiveness, but does not sandbox learner code. A program
can access anything allowed to the user's Windows account unless a separate sandbox is introduced.

## Near-term evolution

1. Add the beginner welcome experience, examples, and recent-file affordances.
2. Add structured error models and deterministic traceback analysis.
