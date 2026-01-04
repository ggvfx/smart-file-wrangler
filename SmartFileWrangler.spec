# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\smart_file_wrangler\\gui.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/smart_file_wrangler/main_window.ui', '.')],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='SmartFileWrangler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch="x64",
    codesign_identity=None,
    entitlements_file=None, 
    icon="assets\\smart-file-wrangler.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='SmartFileWrangler',
)
