# Security Policy

PyNivo is in early development and does not yet have supported production releases.

## Security model

Opening a Python file must never execute it. When execution is implemented, learner code will run
in a separate child process without use of a command shell. This is a reliability boundary, not a
sandbox: Python code intentionally run by the user can read, modify, or transmit data available to
that user's account.

PyNivo does not currently include telemetry, accounts, automatic package installation, or network
services. Application logs must not contain learner source code or secrets by default.

## Reporting

Until a private reporting channel is established, avoid filing public issues containing secrets,
private source code, or exploit details. Repository maintainers should add a private security
contact before the first public release.

