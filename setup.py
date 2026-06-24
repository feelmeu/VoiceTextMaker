"""VoiceTextMaker 安装配置"""

from setuptools import setup, find_packages

setup(
    name="voicetextmaker",
    version="0.1.0",
    description="AI 语音克隆 + 唇形同步视频生成工具",
    author="feelmeu",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "soundfile>=0.12.0",
        "scipy>=1.10.0",
        "pyyaml>=6.0",
        "Pillow>=10.0.0",
        "gradio>=4.0.0",
    ],
    extras_require={
        "tts": ["gpt-sovits-python>=1.0.0"],
        "test": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "voicetextmaker=src.main:main",
        ],
    },
)
