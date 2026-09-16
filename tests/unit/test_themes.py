from pynivo.ui.themes import DARK, LIGHT, stylesheet


def luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def test_themes_have_distinct_accessible_surfaces() -> None:
    assert DARK.editor_background != LIGHT.editor_background
    assert DARK.output_text != DARK.editor_background
    assert LIGHT.output_text != LIGHT.editor_background
    assert "QToolBar#main_toolbar" in stylesheet(DARK)
    assert "QFrame#sideRail" in stylesheet(LIGHT)
    assert luminance(LIGHT.editor_background) < 0.85
    assert abs(luminance(LIGHT.editor_background) - luminance(LIGHT.output_text)) > 0.65
