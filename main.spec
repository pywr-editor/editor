# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from win32com.propsys import propsys

block_cipher = None

# manually copy modules not discovered by PyInstaller
bins = []
win32_module_path = Path(propsys.__file__).parent
bins.append((win32_module_path / "propsys.pyd", "win32com\propsys"))
bins.append((win32_module_path / "pscon.py", "win32com\propsys"))

a = Analysis(
    ["main.py"],
    binaries=bins,
    datas=[
        (
            "LEGAL NOTICES.md",
            ".",
        ),
        ("pywr_editor/assets/ico/Pywr Editor.ico", "."),
    ],
    hiddenimports=[
        "json",
        "pandas",
        "logging",
        "logging.config",
        "pyqtgraph",
        "PySide6.QtSvg",
        "PySide6.QtAxContainer",
        "PySide6.QtSvgWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "jedi", "scipy", "IPython", "sqlite3"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Pywr Editor",
    icon="pywr_editor/assets/ico/Pywr Editor.ico",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="main",
)
