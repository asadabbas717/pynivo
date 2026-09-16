# Bundled Python runtime

Production builds place an official 64-bit Windows CPython embeddable distribution in this
directory in the installed application, renamed/copied to `runtime/` beside the application.
Runtime binaries are deliberately not committed to Git.

The expected minimum layout is:

```text
runtime/
├── python.exe
├── python3.dll
├── python3xx.dll
├── python3xx.zip
└── python3xx._pth
```

Release automation must download a pinned artifact from python.org, verify its published checksum
or Sigstore metadata, extract it without path traversal, retain required license notices, and test
it on a clean Windows 10/11 machine. Never silently download a runtime when PyNivo starts.

The embeddable distribution intentionally excludes pip, Tk, and Python documentation. Its `._pth`
file provides isolation and must not be removed casually. The future package manager must not run
ordinary pip directly against this runtime; third-party packages need a designed, isolated strategy.
