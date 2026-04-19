# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main-DARKZONE.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('lib', 'lib'), # Include the standard library
    ],
    hiddenimports=[
        'torch',
        'sympy',
        'numpy',
        'networkx',
        'matplotlib',
        'sklearn',
        'scipy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.cipher, hook=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='fiber',
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
