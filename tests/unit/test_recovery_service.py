import json
from pathlib import Path

import pytest

from pynivo.core.files import RecoveryDocument, RecoveryService


def test_recovery_round_trip_preserves_unicode_and_paths(tmp_path: Path) -> None:
    service = RecoveryService(tmp_path / "recovery")
    documents = (
        RecoveryDocument(path=None, text="print('سلام')\n"),
        RecoveryDocument(path="C:/lessons/hello.py", text="print('hello')\n"),
    )

    service.save(documents)

    assert service.load() == documents


def test_recovery_clear_removes_snapshot(tmp_path: Path) -> None:
    service = RecoveryService(tmp_path)
    service.save((RecoveryDocument(path=None, text="work"),))

    service.clear()

    assert service.load() == ()


def test_corrupted_recovery_is_ignored(tmp_path: Path) -> None:
    service = RecoveryService(tmp_path)
    service.snapshot_path.write_text("not json", encoding="utf-8")

    assert service.load() == ()


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        1,
        "text",
        {"version": True},
        {"version": 1, "documents": None},
        {"version": 1, "documents": {}},
        {"version": 2, "documents": []},
    ],
)
def test_malformed_snapshot_shapes_are_ignored(tmp_path: Path, payload: object) -> None:
    service = RecoveryService(tmp_path)
    service.snapshot_path.write_text(json.dumps(payload), encoding="utf-8")
    assert service.load() == ()


def test_invalid_entries_do_not_discard_valid_recovery(tmp_path: Path) -> None:
    service = RecoveryService(tmp_path)
    payload = {
        "version": 1,
        "documents": [
            None,
            {"text": 1},
            {"text": "bad", "path": []},
            {"text": "bad", "path": "a\u0000.py"},
            {"text": "retained", "path": None},
        ],
    }
    service.snapshot_path.write_text(json.dumps(payload), encoding="utf-8")
    assert service.load() == (RecoveryDocument(None, "retained"),)
