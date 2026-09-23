from pathlib import Path

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
