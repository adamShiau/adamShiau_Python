# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\github\\ThermalCycling\\SG_AHRS_TTC\\SG_AHRS_01_07_TTC_RW(can_open_more)\\pigImu_Main.py'],
    pathex=['C:\\github\\ThermalCycling\\SG_AHRS_TTC\\SG_AHRS_01_07_TTC_RW(can_open_more)\\myLib', '.'],
    binaries=[],
    datas=[],
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
    name='pigImu_Main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
