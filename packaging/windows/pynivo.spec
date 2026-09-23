from pathlib import Path

project_root = Path(SPECPATH).parents[1]

a = Analysis(
    [str(project_root / "packaging" / "windows" / "entrypoint.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=[
        (str(project_root / "src" / "pynivo" / "learning" / "data" / "*.json"), "pynivo/learning/data"),
        (str(project_root / "resources" / "branding" / "pynivo.ico"), "resources/branding"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PyNivo",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(project_root / "resources" / "branding" / "pynivo.ico"),
    version=str(project_root / "packaging" / "windows" / "version_info.txt"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="PyNivo",
)
