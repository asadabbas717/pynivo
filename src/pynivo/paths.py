"""Stable application and resource paths for source and frozen builds."""

from __future__ import annotations

import sys
from pathlib import Path


def application_root() -> Path:
    """Return the folder that owns the private learner runtime."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resource_path(relative_path: str) -> Path:
    """Resolve a bundled read-only resource in either execution mode."""
    bundle_root = Path(getattr(sys, "_MEIPASS", application_root()))
    return bundle_root / relative_path
