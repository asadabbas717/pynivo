"""Compile the verified portable build into a per-user Windows installer."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def find_compiler() -> Path | None:
    on_path = shutil.which("ISCC.exe") or shutil.which("ISCC")
    candidates = [
        Path(on_path) if on_path else None,
        Path.home() / "AppData" / "Local" / "Programs" / "Inno Setup 7" / "ISCC.exe",
        Path(r"C:\Program Files\Inno Setup 7\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
    ]
    return next((path for path in candidates if path is not None and path.is_file()), None)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-portable",
        action="store_true",
        help="Reuse an existing verified dist/PyNivo directory.",
    )
    options = parser.parse_args()
    project_root = Path(__file__).resolve().parents[2]
    if not options.skip_portable:
        subprocess.run(
            [sys.executable, str(project_root / "packaging" / "windows" / "build.py")],
            cwd=project_root,
            check=True,
        )
    compiler = find_compiler()
    if compiler is None:
        raise RuntimeError(
            "Inno Setup is not installed. Install Inno Setup 7, then rerun this command."
        )
    script = project_root / "packaging" / "windows" / "pynivo.iss"
    subprocess.run([str(compiler), str(script)], cwd=project_root, check=True)
    print(f"Installer created in {project_root / 'dist' / 'installer'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
