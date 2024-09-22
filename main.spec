# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None
path = os.path.abspath(".")

datas = [
    (os.path.join(path, 'edit_icon.png'), '.'),  # Changed from .png to .icns
]

a = Analysis(
    ['main.py'],
    pathex=[path],  # Ensure absolute path
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt6',                # Ensure PyQt6 is included
        'PyQt6.QtCore',         # PyQt6 core modules
        'PyQt6.QtGui',          # PyQt6 GUI components
        'PyQt6.QtWidgets',      # PyQt6 widget components
        'PyQt6.QtPrintSupport', # Include print support if required
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # Remove or set to None since icon is set in BUNDLE
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app'
)

app = BUNDLE(
    coll,
    name='MusicPractice.app',
    icon=os.path.join(path, 'myapp.icns'),  # Set the icon path
    bundle_identifier=None
)
