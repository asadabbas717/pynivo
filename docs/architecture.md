# Architecture

PyNivo uses a `src` package layout and keeps framework-dependent UI code separate from core
application logic.

## Boundaries

- `pynivo.ui` owns Qt widgets and user interaction.
- `pynivo.core.runtime` locates and validates Python runtimes. The current system-runtime
  implementation is for development; a bundled-runtime implementation can satisfy the same
  protocol later.
- `pynivo.core.execution` describes validated child-process launches. A later QProcess service
  will consume these requests and own stdout, stderr, stdin, stopping, and process state.
- `pynivo.app` is the composition root. It starts logging, Qt, and the main window.

Core modules do not import Qt. This keeps validation logic fast to test and prevents UI concerns
from leaking into future runtime, file, error-analysis, and learning services.

## Execution security boundary

Learner programs will run as separate processes and will never be imported into the GUI process.
Arguments are represented structurally and are not concatenated into a shell command. Process
separation improves reliability and responsiveness, but does not sandbox learner code. A program
can access anything allowed to the user's Windows account unless a separate sandbox is introduced.

## Near-term evolution

1. Add an editor component and document/file service with atomic UTF-8 saves.
2. Add a QProcess-backed execution service using `ExecutionRequest`.
3. Add output and input widgets without turning the panel into a general-purpose shell.
4. Add structured error models and deterministic traceback analysis.

