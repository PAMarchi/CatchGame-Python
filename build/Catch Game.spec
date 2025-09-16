# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['game.py'],
    pathex=[],
    binaries=[],
    datas=[('rotten_lemon.png', '.'), ('rotten_apple.png', '.'), ('banana.png', '.'), ('apple.png', '.'), ('orange_1.png', '.'), ('orange_2.png', '.'), ('mango.png', '.'), ('background.png', '.'), ('life.png', '.'), ('catching_se.mp3', '.'), ('basket.png', '.'), ('basket.ico', '.')],
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
    a.binaries,
    a.datas,
    [],
    name='Catch Game',
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
    icon=['basket.ico'],
)
