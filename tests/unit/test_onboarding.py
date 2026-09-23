from pynivo.ui.onboarding import should_show_welcome


def test_welcome_is_shown_once_for_each_release() -> None:
    assert should_show_welcome(None, "0.1.0")
    assert not should_show_welcome("0.1.0", "0.1.0")
    assert should_show_welcome("0.1.0", "0.2.0")


def test_smoke_tests_never_consume_onboarding() -> None:
    assert not should_show_welcome(None, "0.1.0", onboarding_enabled=False)
