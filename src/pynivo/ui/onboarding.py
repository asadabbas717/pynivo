"""First-run onboarding policy kept separate from window construction."""


def should_show_welcome(
    seen_version: str | None,
    current_version: str,
    *,
    onboarding_enabled: bool = True,
) -> bool:
    """Show onboarding once per release, except during automated smoke tests."""
    return onboarding_enabled and seen_version != current_version
