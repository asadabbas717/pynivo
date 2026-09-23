from pynivo.ui.dialogs.about_dialog import installed_notice


def test_installed_license_and_notices_are_available() -> None:
    assert "Apache License" in installed_notice("LICENSE")
    assert "Qt for Python" in installed_notice("THIRD_PARTY_NOTICES.md")
