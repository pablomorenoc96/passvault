# -*- mode: python ; coding: utf-8 -*-
"""Receta de PyInstaller.  Compilar con:  pyinstaller gestor_passwords.spec"""

a = Analysis(
    ['gestor_passwords.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/gestor.ico', 'assets')],
    hiddenimports=[
        'argon2',
        'argon2.low_level',
        'openpyxl',
        'openpyxl.cell._writer',
        'cryptography.hazmat.primitives.ciphers.aead',
        'cryptography.hazmat.primitives.kdf.scrypt',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # La app no usa pandas ni numpy: excluirlos baja el .exe de ~180 MB a ~25 MB.
    excludes=[
        'pandas', 'numpy', 'matplotlib', 'scipy', 'PIL', 'pytest',
        'setuptools', 'pip', 'tkinter.test', 'test', 'unittest',
    ],
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
    name='Gestor de Contrasenas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # sin ventana negra de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/gestor.ico',
)
