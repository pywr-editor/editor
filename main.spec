# -*- mode: python ; coding: utf-8 -*-
import os
import shutil
from pathlib import Path

import pywr
from win32com.propsys import propsys

block_cipher = None

win32_module_path = Path(propsys.__file__).parent
pywr_dist = list(Path(pywr.__file__).parent.parent.glob("pywr-*"))[0]

a = Analysis(
    ["main.py"],
    binaries=[
        (win32_module_path / "propsys.pyd", "win32com\propsys"),
        (win32_module_path / "pscon.py", "win32com\propsys"),
        (Path(os.environ["VIRTUAL_ENV"]) / "bin" / "libblosc2.dll", "tables"),
    ],
    datas=[
        ("LEGAL NOTICES.md", "."),
        ("pywr_editor/assets/ico/Pywr Editor.ico", "."),
        # Pywr hidden imports are not copied. Copy the full package content
        (Path(pywr.__file__).parent, "pywr"),
        # pywr __init__.py relies on the dist info folder to set __version__.
        # This must be manually copied
        # (pywr_dist.as_posix(), pywr_dist.name),
    ],
    hiddenimports=[
        "json",
        "pandas",
        "logging",
        "logging.config",
        "pyqtgraph",
        "tables",
        "pywr",
        "pkg_resources",
        "platformdirs",
        "PySide6.QtSvg",
        "PySide6.QtAxContainer",
        "PySide6.QtSvgWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "jedi", "IPython", "sqlite3"],
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

# PyInstaller does not want to copy the dist info folder (see datas attribute)
shutil.copytree(pywr_dist.as_posix(), f"./dist/main/{pywr_dist.name}")
