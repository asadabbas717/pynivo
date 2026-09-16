from pathlib import Path

import pytest

from pynivo.core.files import DocumentError, DocumentService


def test_save_adds_python_extension_and_loads_unicode(tmp_path: Path) -> None:
    service = DocumentService()
    text = 'message = "سلام، Python!"\n'

    saved = service.save(tmp_path / "lesson", text)
    loaded = service.load(saved.path)

    assert saved.path == (tmp_path / "lesson.py").resolve()
    assert loaded.text == text


def test_save_replaces_existing_content_without_leaving_temp_file(tmp_path: Path) -> None:
    service = DocumentService()
    destination = tmp_path / "program.py"
    destination.write_text("old\n", encoding="utf-8")

    service.save(destination, "new\n")

    assert destination.read_text(encoding="utf-8") == "new\n"
    assert list(tmp_path.glob("*.tmp")) == []


def test_load_accepts_utf8_byte_order_mark(tmp_path: Path) -> None:
    source = tmp_path / "bom.py"
    source.write_bytes(b"\xef\xbb\xbfprint('hello')\n")

    document = DocumentService().load(source)

    assert document.text == "print('hello')\n"


def test_load_rejects_non_python_file(tmp_path: Path) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("hello", encoding="utf-8")

    with pytest.raises(DocumentError, match=r"\.py"):
        DocumentService().load(source)


def test_load_reports_invalid_utf8(tmp_path: Path) -> None:
    source = tmp_path / "broken.py"
    source.write_bytes(b"\xff\xfe")

    with pytest.raises(DocumentError, match="Could not open"):
        DocumentService().load(source)
