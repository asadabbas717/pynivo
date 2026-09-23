import hashlib
from pathlib import Path


def test_canonical_lgpl_license_files_are_unchanged() -> None:
    expected = {
        "LGPL-3.0-only.txt": "da7eabb7bafdf7d3ae5e9f223aa5bdc1eece45ac569dc21b3b037520b4464768",
        "GPL-3.0-only.txt": "8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903",
    }

    for filename, digest in expected.items():
        text = (Path("licenses") / filename).read_text(encoding="utf-8")
        content = text.replace("\r\n", "\n").encode("utf-8")
        assert hashlib.sha256(content).hexdigest() == digest


def test_qt_compliance_notice_names_exact_sources() -> None:
    notice = Path("QT_LGPL_COMPLIANCE.md").read_text(encoding="utf-8")

    assert "PySide6 / Shiboken 6.11.2" in notice
    assert "Qt 6.11.2 complete source" in notice
    assert "_internal/PySide6" in notice
