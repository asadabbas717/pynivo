# Qt / PySide6 LGPL compliance

PyNivo 0.1.0 uses the unmodified Qt for Python (PySide6) 6.11.2 Community
Edition under the GNU Lesser General Public License version 3 (LGPLv3).
PyNivo itself remains licensed under Apache License 2.0.

The Qt and PySide libraries are dynamically loaded from `_internal/PySide6`
and `_internal/shiboken6` in the installed application. PyNivo does not apply
technical restrictions that prevent replacing those libraries or reverse
engineering for the purpose of debugging a modified LGPL library.

## Replacing the LGPL libraries

1. Close PyNivo.
2. Back up the installed `_internal/PySide6` and `_internal/shiboken6`
   directories.
3. Build an interface-compatible PySide6/Qt 6.11.2 distribution for 64-bit
   Windows, or obtain one from the Qt for Python project.
4. Replace the corresponding DLL and PYD files in those directories while
   preserving their filenames and relative paths.
5. Start PyNivo and test the modified libraries.

The replacement libraries must remain binary-compatible with the Python 3.13
ABI and the interfaces used by PyNivo. These instructions do not provide a
warranty for modified builds.

## Corresponding source

The exact upstream source releases used by this build are available from the
Qt Project:

- PySide6 / Shiboken 6.11.2:
  https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.11.2-src/pyside-setup-everywhere-src-6.11.2.tar.xz
  SHA-256: `cba47efbaad1bedd529725cbc14e21f156c7a19366f07b3edfbb076ffd7afdf8`
- Qt 6.11.2 complete source:
  https://download.qt.io/archive/qt/6.11/6.11.2/single/qt-everywhere-src-6.11.2.tar.xz
  SHA-256: `6dcfbca271d76a6502741a2c0dc6fc98ef7dd0b7b4cfd0abcebb285a86a26f33`

No modifications have been made to the Qt, PySide6, or Shiboken libraries.
If an upstream URL becomes unavailable, request the corresponding source by
opening an issue at https://github.com/asadabbas717/pynivo/issues. This offer
is valid for at least three years after the last distribution of this version.

The complete LGPLv3 and GPLv3 texts are included in the `licenses` directory.
