# Third-party notices

PyNivo distributions include components maintained by other projects. This file is informational;
the complete corresponding license texts must remain in the distributed application.

PyNivo itself is licensed under the Apache License 2.0. See `LICENSE` and `NOTICE` in the
application directory.

## Python

The private learner runtime is the official CPython Windows embeddable distribution. Python is
distributed under the Python Software Foundation License Version 2 and other historical licenses.
The runtime's `LICENSE.txt` is included unchanged inside the `runtime` directory.

## Qt for Python / PySide6

PyNivo includes the unmodified Qt for Python (PySide6), Shiboken6, and Qt 6.11.2 libraries under
the GNU Lesser General Public License version 3. The libraries are dynamically loaded and may be
replaced with compatible builds. See `QT_LGPL_COMPLIANCE.md` for source locations, checksums, and
replacement instructions. The complete LGPLv3 and incorporated GPLv3 terms are in `licenses`.

## PyInstaller

PyInstaller is used only as a build tool. Its bootloader exception permits distributing generated
applications under the application's chosen license, subject to PyInstaller's license terms.
