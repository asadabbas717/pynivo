from pynivo.ui.themes import DARK, LIGHT, stylesheet


def test_themes_have_distinct_accessible_surfaces() -> None:
    assert DARK.editor_background != LIGHT.editor_background
    assert DARK.output_text != DARK.editor_background
    assert LIGHT.output_text != LIGHT.editor_background
    assert "QToolBar#main_toolbar" in stylesheet(DARK)
    assert "QFrame#sideRail" in stylesheet(LIGHT)
