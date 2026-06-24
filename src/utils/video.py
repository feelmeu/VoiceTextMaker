"""视频工具函数"""

import subprocess
from pathlib import Path

from .logger import get_logger

logger = get_logger("video_utils")


class VideoUtils:
    """视频处理工具类"""

    @staticmethod
    def get_info(video_path: Path) -> dict:
        """获取视频信息

        Returns:
            dict: {fps, width, height, duration, codec}
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            str(video_path),
        ]
        import json
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        info = json.loads(result.stdout)

        video_stream = None
        for s in info.get("streams", []):
            if s.get("codec_type") == "video":
                video_stream = s
                break

        fps = 25
        if video_stream:
            r_fps = video_stream.get("r_frame_rate", "25/1")
            num, den = map(int, r_fps.split("/"))
            fps = num / den if den else 25

        return {
            "fps": fps,
            "width": int(video_stream.get("width", 0)) if video_stream else 0,
            "height": int(video_stream.get("height", 0)) if video_stream else 0,
            "duration": float(info.get("format", {}).get("duration", 0)),
            "codec": video_stream.get("codec_name", "") if video_stream else "",
        }

    @staticmethod
    def convert_fps(input_path: Path, output_path: Path, target_fps: int = 25) -> Path:
        """转换视频帧率

        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            target_fps: 目标帧率

        Returns:
            输出文件路径
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-vf", f"fps={target_fps}",
            "-c:a", "copy",
            str(output_path),
        ]
        subprocess.run(cmd, capture_output=True, check=True, timeout=120)
        return output_path

    @staticmethod
    def merge_audio_video(
        video_path: Path,
        audio_path: Path,
        output_path: Path,
    ) -> Path:
        """合并音频和视频

        Args:
            video_path: 输入视频路径
            audio_path: 输入音频路径
            output_path: 输出视频路径

        Returns:
            输出文件路径
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            str(output_path),
        ]
        subprocess.run(cmd, capture_output=True, check=True, timeout=120)
        return output_path
