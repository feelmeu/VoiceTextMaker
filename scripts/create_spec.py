"""生成 PyInstaller spec 文件"""

import sys
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def create_spec():
    """创建 PyInstaller spec 文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# VoiceTextMaker PyInstaller spec 文件

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('examples', 'examples'),
    ],
    hiddenimports=[
        'gradio',
        'torch',
        'torchaudio',
        'cv2',
        'numpy',
        'scipy',
        'yaml',
        'PIL',
        'soundfile',
        'src.core',
        'src.tts',
        'src.lipsync',
        'src.gui',
        'src.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'notebook',
        'IPython',
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
    [],
    exclude_binaries=True,
    name='VoiceTextMaker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VoiceTextMaker',
)
'''

    spec_dir = ROOT / "dist"
    spec_dir.mkdir(exist_ok=True)
    spec_path = spec_dir / "VoiceTextMaker.spec"
    spec_path.write_text(spec_content, encoding="utf-8")
    print(f"Spec file created: {spec_path}")


if __name__ == "__main__":
    create_spec()
