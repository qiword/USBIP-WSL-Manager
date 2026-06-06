# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

sys.setrecursionlimit(5000)

block_cipher = None

# 收集数据文件
datas = []
# SVG 图标
icon_svg = Path("icon.svg")
if icon_svg.exists():
    datas.append((str(icon_svg), "."))

a = Analysis(
    ["main.pyw"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "qfluentwidgets",
        "utils.constants",
        "utils.usbip_manager",
        "utils.i18n",
        "utils.autostart",
        "widgets.device_table",
        "widgets.device_menu",
        "widgets.cmd_thread",
        "windows.pages.home_page",
        "windows.pages.settings_page",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="USBIP-WSL-Manager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="icon.ico",
    manifest="admin.manifest",
)
