import importlib.util
import zipfile
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "windows_build", Path(__file__).resolve().parents[2] / "packaging/windows/build.py"
)
assert _SPEC and _SPEC.loader
build = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(build)


def test_checksum_failure_removes_bad_cached_archive(tmp_path):
    archive = tmp_path / build.RUNTIME_NAME
    archive.write_bytes(b"invalid archive")
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        build.verified_runtime_archive(tmp_path)
    assert not archive.exists()


@pytest.mark.parametrize("name", ["../escape.txt", "nested/../../escape.txt"])
def test_archive_traversal_is_rejected_before_extraction(tmp_path, name):
    archive = tmp_path / "runtime.zip"
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("valid.txt", "valid")
        package.writestr(name, "unsafe")
    destination = tmp_path / "extracted"
    with pytest.raises(RuntimeError, match="Unsafe path"):
        build.safe_extract(archive, destination)
    assert not (destination / "valid.txt").exists()
    assert not (tmp_path / "escape.txt").exists()


def test_missing_distribution_fails_before_smoke_launch(tmp_path):
    with pytest.raises(RuntimeError, match="PyNivo.exe"):
        build.verify_distribution(tmp_path, expect_runtime=True)
