"""Central light and dark visual themes for PyNivo."""

# ruff: noqa: E501 - QSS rules remain readable as one selector per line.

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True, slots=True)
class Theme:
    name: str
    editor_background: str
    gutter_background: str
    gutter_text: str
    current_line: str
    output_text: str
    error_text: str
    syntax: tuple[str, str, str, str, str]


DARK = Theme(
    "dark",
    "#090D12",
    "#0D131A",
    "#536373",
    "#111C25",
    "#B9F6E5",
    "#FF6B81",
    ("#C792EA", "#4DD7FA", "#F9C74F", "#60788A", "#5FFFB0"),
)
LIGHT = Theme(
    "light",
    "#D5DCDE",
    "#C5CED1",
    "#425960",
    "#C7DAD5",
    "#173B3B",
    "#A61B3B",
    ("#6037A3", "#005F7A", "#8A4D00", "#5B7078", "#087458"),
)


def stylesheet(theme: Theme) -> str:
    dark = theme.name == "dark"
    bg, panel, raised = (
        ("#070A0E", "#0C1118", "#111923") if dark else ("#B9C4C7", "#C5CED1", "#D3DADC")
    )
    text, muted, border = (
        ("#D6E7E3", "#718A92", "#1D3038") if dark else ("#10272E", "#405A62", "#93A5AA")
    )
    return f"""
    QMainWindow, QDialog {{ background: {bg}; color: {text}; }}
    QWidget {{ color: {text}; font-family: "Segoe UI"; font-size: 10pt; }}
    QMenuBar {{ background: {bg}; border-bottom: 1px solid {border}; padding: 3px; }}
    QMenuBar::item:selected, QMenu::item:selected {{ background: #00BFA522; color: #21E6C1; }}
    QMenu {{ background: {raised}; border: 1px solid {border}; padding: 6px; }}
    QMenu::item {{ padding: 7px 24px 7px 10px; }}
    QToolBar#main_toolbar {{ background: {panel}; border: 0; border-bottom: 1px solid {border}; spacing: 6px; padding: 7px 12px; }}
    QToolButton {{ padding: 7px 12px; border-radius: 5px; color: {text}; }}
    QToolButton:hover {{ background: #00BFA522; color: #21E6C1; }}
    QToolButton:disabled {{ color: {muted}; }}
    QTabWidget::pane {{ border: 1px solid {border}; background: {theme.editor_background}; }}
    QTabBar {{ background: {panel}; }}
    QTabBar::tab {{ background: {panel}; color: {muted}; padding: 9px 18px; border-right: 1px solid {border}; }}
    QTabBar::tab:selected {{ background: {theme.editor_background}; color: #21E6C1; border-top: 2px solid #21E6C1; }}
    QPlainTextEdit {{ background: {theme.editor_background}; color: {text}; border: 0; selection-background-color: #007F6F; }}
    QListWidget, QListView, QTreeWidget, QTableWidget {{ background: {raised}; color: {text}; border: 1px solid {border}; border-radius: 5px; outline: 0; }}
    QAbstractItemView::item {{ color: {text}; padding: 8px; border-radius: 3px; }}
    QAbstractItemView::item:hover {{ background: #00A88F22; color: {text}; }}
    QAbstractItemView::item:selected {{ background: #007F6F; color: #FFFFFF; }}
    QLineEdit {{ background: {raised}; color: {text}; border: 1px solid {border}; border-radius: 5px; padding: 8px; }}
    QPushButton {{ background: {raised}; color: {text}; border: 1px solid {border}; border-radius: 5px; padding: 8px 14px; }}
    QPushButton:hover {{ border-color: #21E6C1; color: #0BAF96; }}
    QPushButton#primaryButton {{ background: #00A88F; color: white; border: 1px solid #21E6C1; font-weight: 600; }}
    QSplitter::handle {{ background: {border}; height: 2px; }}
    QStatusBar {{ background: {panel}; color: {muted}; border-top: 1px solid {border}; }}
    QLabel#brand {{ color: #21E6C1; font-size: 16pt; font-weight: 700; letter-spacing: 2px; }}
    QLabel#sectionTitle {{ color: {muted}; font-size: 9pt; font-weight: 600; }}
    QToolTip {{ background: {raised}; color: {text}; border: 1px solid {border}; padding: 5px; }}
    QFrame#sideRail {{ background: {panel}; border-right: 1px solid {border}; }}
    QFrame#consoleFrame {{ background: {panel}; border: 1px solid {border}; border-radius: 7px; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; }}
    QScrollBar::handle:vertical {{ background: {border}; border-radius: 5px; min-height: 25px; }}
    """


def apply_theme(application: QApplication, name: str) -> Theme:
    theme = LIGHT if name == "light" else DARK
    dark = theme.name == "dark"
    window = "#070A0E" if dark else "#B9C4C7"
    base = theme.editor_background
    text = "#D6E7E3" if dark else "#10272E"
    button = "#111923" if dark else "#D3DADC"
    disabled = "#718A92" if dark else "#60747A"
    palette = QPalette()
    for role, color in (
        (QPalette.ColorRole.Window, window),
        (QPalette.ColorRole.WindowText, text),
        (QPalette.ColorRole.Base, base),
        (QPalette.ColorRole.AlternateBase, button),
        (QPalette.ColorRole.Text, text),
        (QPalette.ColorRole.Button, button),
        (QPalette.ColorRole.ButtonText, text),
        (QPalette.ColorRole.Highlight, "#007F6F"),
        (QPalette.ColorRole.HighlightedText, "#FFFFFF"),
        (QPalette.ColorRole.PlaceholderText, disabled),
    ):
        palette.setColor(role, QColor(color))
    application.setPalette(palette)
    application.styleHints().setColorScheme(Qt.ColorScheme.Dark if dark else Qt.ColorScheme.Light)
    application.setStyleSheet(stylesheet(theme))
    return theme
