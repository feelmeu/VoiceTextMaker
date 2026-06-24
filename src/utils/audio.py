"""音频工具函数"""

import subprocess
from pathlib import Path
from typing import Optional

from .logger import get_logger

logger = get_logger("audio_utils")


class AudioUtils:
    """音频处理工具类"""

    @staticmethod
    def get_duration(audio_path: Path) -> float:
        """获取音频时长（秒）"""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            str(audio_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return float(result.stdout.strip())

    @staticmethod
    def convert(
        input_path: Path,
        output_path: Path,
        sample_rate: int = 16000,
        channels: int = 1,
        format: str = "wav",
    ) -> Path:
        """转换音频格式/采样率

        Args:
            input_path: 输入音频路径
            output_path: 输出音频路径
            sample_rate: 目标采样率
            channels: 声道数
            format: 输出格式

        Returns:
            输出文件路径
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-ar", str(sample_rate),
            "-ac", str(channels),
            "-f", format,
            str(output_path),
        ]
        logger.debug(f"Audio convert: {' '.join(cmd)}")
        subprocess.run(cmd, capture_output=True, check=True, timeout=60)
        return output_path

    @staticmethod
    def extract_from_video(video_path: Path, output_path: Path) -> Path:
        """从视频中提取音频

        Args:
            video_path: 输入视频路径
            output_path: 输出音频路径

        Returns:
            输出文件路径
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            str(output_path),
        ]
        subprocess.run(cmd, capture_output=True, check=True, timeout=120)
        return output_path
