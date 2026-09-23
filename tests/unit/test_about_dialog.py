from pynivo.ui.dialogs.about_dialog import installed_notice


def test_installed_license_and_notices_are_available() -> None:
    license_notice = installed_notice("LICENSE_NOTICE.txt")
    assert "Copyright 2026 Asad Abbas" in license_notice
    assert "[yyyy]" not in license_notice
    assert "Qt for Python" in installed_notice("THIRD_PARTY_NOTICES.md")
