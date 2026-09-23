from pathlib import Path


def test_installer_displays_product_notice_and_forces_post_install_welcome() -> None:
    script = Path("packaging/windows/pynivo.iss").read_text(encoding="utf-8")

    assert "LicenseFile=..\\..\\LICENSE_NOTICE.txt" in script
    assert 'Parameters: "--welcome"' in script


def test_unsigned_preview_warning_is_explicit() -> None:
    notice = Path("UNSIGNED_PREVIEW.md").read_text(encoding="utf-8")
    normalized_notice = " ".join(notice.split())

    assert "not digitally signed" in notice
    assert "Unknown publisher" in normalized_notice
    assert "SHA256SUMS.txt" in notice
