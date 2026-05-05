# -*- mode: python ; coding: utf-8 -*-
"""
Spec PyInstaller — Factor Z Gás Natural
Engenharia de Reservatórios I — 2025/2026 — ISPTEC
Docente: Geraldo Ramos, BSc, MSc, PhD

Reconstruir:
    pyinstaller FactorZ_GasNatural.spec
"""

from pathlib import Path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[
        # ícone incluído no executável
        ('icon.ico', '.'),
        # pacote de módulos de cálculo
        ('modules/__init__.py',    'modules'),
        ('modules/properties.py',  'modules'),
        ('modules/correlations.py','modules'),
        ('modules/viscosidade.py', 'modules'),
        ('modules/volumetria.py',  'modules'),
    ],
    hiddenimports=[
        # módulos de cálculo
        'modules',
        'modules.properties',
        'modules.correlations',
        'modules.viscosidade',
        'modules.volumetria',
        # tkinter completo
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        '_tkinter',
        # matplotlib + backend Tk
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends._backend_tk',
        'matplotlib.figure',
        'matplotlib.axes',
        'matplotlib.ticker',
        'matplotlib.font_manager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # excluir partes de scipy/numpy não utilizadas para reduzir tamanho
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'PIL',
        'PyQt5',
        'PyQt6',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FactorZ_GasNatural',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                 # sem janela de consola preta
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
