"""MuseTalk LipSync Provider 实现"""

import subprocess
from pathlib import Path

from ..core.lipsync_provider import LipSyncProvider, LipSyncResult
from ..utils.logger import get_logger

logger = get_logger("musetalk")


class MuseTalkProvider(LipSyncProvider):
    """MuseTalk 唇形同步提供者

    基于 MuseTalk 推理脚本实现。
    参考: https://github.com/TMElyralab/MuseTalk
    """

    def __init__(self):
        self._model_path: Path = None
        self._loaded = False
        self._version: str = "v15"  # 默认使用 1.5 版本
        self._ffmpeg_path: str = "ffmpeg"

    def load_model(self, model_path: Path, **kwargs) -> None:
        """加载 MuseTalk 模型

        Args:
            model_path: MuseTalk 根目录
            **kwargs:
                version: "v15" 或 "v1"
                ffmpeg_path: FFmpeg 路径
        """
        logger.info(f"Loading MuseTalk from {model_path}")
        self._model_path = model_path
        self._version = kwargs.get("version", "v15")
        self._ffmpeg_path = kwargs.get("ffmpeg_path", "ffmpeg")

        # 验证模型文件存在
        if self._version == "v15":
            unet_path = model_path / "models" / "musetalkV15" / "unet.pth"
        else:
            unet_path = model_path / "models" / "musetalk" / "pytorch_model.bin"

        if not unet_path.exists():
            raise FileNotFoundError(f"MuseTalk 模型文件不存在: {unet_path}")

        self._loaded = True
        logger.info(f"MuseTalk {self._version} loaded successfully")

    def generate(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        **kwargs,
    ) -> LipSyncResult:
        """生成唇形同步视频"""
        if not self._loaded:
            raise RuntimeError("模型未加载，请先调用 load_model()")

        logger.info(f"Generating lip sync: video={video_path}, audio={audio_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_dir = output_path.parent / "musetalk_result"
        result_dir.mkdir(parents=True, exist_ok=True)

        # 构建推理配置
        face_size = kwargs.get("face_size", 256)

        # 构建推理命令
        if self._version == "v15":
            unet_path = self._model_path / "models" / "musetalkV15" / "unet.pth"
            unet_config = self._model_path / "models" / "musetalkV15" / "musetalk.json"
        else:
            unet_path = self._model_path / "models" / "musetalk" / "pytorch_model.bin"
            unet_config = self._model_path / "models" / "musetalk" / "musetalk.json"

        cmd = [
            "python", "-m", "scripts.inference",
            "--inference_config", str(self._get_inference_config(video_path, audio_path)),
            "--result_dir", str(result_dir),
            "--unet_model_path", str(unet_path),
            "--unet_config", str(unet_config),
            "--version", self._version,
            "--ffmpeg_path", self._ffmpeg_path,
        ]

        logger.debug(f"Running: {' '.join(cmd)}")
        subprocess.run(
            cmd,
            cwd=str(self._model_path),
            capture_output=True,
            check=True,
            timeout=600,
        )

        # 找到输出视频
        result_videos = list(result_dir.glob("*.mp4"))
        if not result_videos:
            raise RuntimeError("MuseTalk 未生成输出视频")

        # 移动到目标位置
        import shutil
        shutil.move(str(result_videos[0]), str(output_path))

        # 获取视频信息
        from ..utils.video import VideoUtils
        info = VideoUtils.get_info(output_path)

        return LipSyncResult(
            video_path=output_path,
            fps=info["fps"],
            duration=info["duration"],
            resolution=(info["width"], info["height"]),
        )

    def _get_inference_config(self, video_path: Path, audio_path: Path) -> Path:
        """生成推理配置文件"""
        import yaml

        config = {
            "video_path": str(video_path),
            "audio_path": str(audio_path),
        }

        config_path = self._model_path / "configs" / "inference" / "vtm_inference.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(yaml.dump(config), encoding="utf-8")
        return config_path

    def is_loaded(self) -> bool:
        return self._loaded

    def unload(self) -> None:
        self._model_path = None
        self._loaded = False
        logger.info("MuseTalk unloaded")
