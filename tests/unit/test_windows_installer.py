from pathlib import Path


def test_installer_displays_product_notice_and_forces_post_install_welcome() -> None:
    script = Path("packaging/windows/pynivo.iss").read_text(encoding="utf-8")

    assert "LicenseFile=..\\..\\LICENSE_NOTICE.txt" in script
    assert 'Parameters: "--welcome"' in script
