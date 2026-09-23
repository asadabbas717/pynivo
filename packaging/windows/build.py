"""Build a verified portable Windows distribution of PyNivo."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

PYTHON_VERSION = "3.13.15"
RUNTIME_NAME = f"python-{PYTHON_VERSION}-embed-amd64.zip"
RUNTIME_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/{RUNTIME_NAME}"
RUNTIME_SHA256 = "d1f04d990aee1253d8569e8e5104e30fa9f5fa830899f14843448872d936a2cf"


def verified_runtime_archive(cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / RUNTIME_NAME
    if not archive.exists():
        print(f"Downloading official CPython {PYTHON_VERSION} embeddable runtime...")
        urllib.request.urlretrieve(RUNTIME_URL, archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != RUNTIME_SHA256:
        archive.unlink(missing_ok=True)
        raise RuntimeError(
            f"Runtime checksum mismatch: expected {RUNTIME_SHA256}, received {digest}"
        )
    return archive


def safe_extract(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(archive) as package:
        for member in package.infolist():
            target = (destination / member.filename).resolve()
            if root not in target.parents and target != root:
                raise RuntimeError(f"Unsafe path in runtime archive: {member.filename}")
        package.extractall(destination)


def build(project_root: Path, *, skip_runtime: bool) -> Path:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--distpath",
            str(project_root / "dist"),
            "--workpath",
            str(project_root / "build"),
            str(project_root / "packaging" / "windows" / "pynivo.spec"),
        ],
        cwd=project_root,
        check=True,
    )
    distribution = project_root / "dist" / "PyNivo"
    if not skip_runtime:
        runtime = distribution / "runtime"
        if runtime.exists():
            if runtime.resolve().parent != distribution.resolve():
                raise RuntimeError(f"Refusing to replace runtime outside build: {runtime}")
            shutil.rmtree(runtime)
        archive = verified_runtime_archive(project_root / "build" / "downloads")
        safe_extract(archive, runtime)
    shutil.copy2(project_root / "THIRD_PARTY_NOTICES.md", distribution)
    verify_distribution(distribution, expect_runtime=not skip_runtime)
    return distribution


def verify_distribution(distribution: Path, *, expect_runtime: bool) -> None:
    executable = distribution / "PyNivo.exe"
    if not executable.is_file():
        raise RuntimeError("PyNivo.exe was not created")
    if expect_runtime:
        runtime = distribution / "runtime" / "python.exe"
        license_file = distribution / "runtime" / "LICENSE.txt"
        if not license_file.is_file():
            raise RuntimeError("The CPython license is missing from the distribution")
        result = subprocess.run(
            [str(runtime), "-I", "-c", "print('PYNIVO_RUNTIME_OK')"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
        )
        if result.returncode != 0 or result.stdout.strip() != "PYNIVO_RUNTIME_OK":
            raise RuntimeError(f"Bundled runtime smoke test failed: {result.stderr.strip()}")
    result = subprocess.run([str(executable), "--smoke-test"], timeout=30, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Packaged application exited with code {result.returncode}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-runtime",
        action="store_true",
        help="Build the GUI without the learner runtime (development diagnostics only).",
    )
    options = parser.parse_args()
    project_root = Path(__file__).resolve().parents[2]
    distribution = build(project_root, skip_runtime=options.skip_runtime)
    print(f"Portable build created at {distribution}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
