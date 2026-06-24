"""MuseTalk LipSync Provider 实现"""

import subprocess
import yaml
from pathlib import Path

from ..core.lipsync_provider import LipSyncProvider, LipSyncResult
from ..utils.logger import get_logger

logger = get_logger("musetalk")


class MuseTalkProvider(LipSyncProvider):
    """MuseTalk 唇形同步提供者

    基于 MuseTalk v1.5 推理脚本实现。
    参考: https://github.com/TMElyralab/MuseTalk

    模型目录结构:
    musetalk_root/
    ├── models/
    │   ├── musetalkV15/
    │   │   ├── unet.pth
    │   │   └── musetalk.json
    │   ├── sd-vae/
    │   ├── whisper/
    │   ├── dwpose/
    │   ├── face-parse-bisent/
    │   └── syncnet/
    ├── configs/inference/
    └── scripts/
    """

    def __init__(self):
        self._model_path: Path = None
        self._loaded = False
        self._version: str = "v15"
        self._ffmpeg_path: str = "ffmpeg"

    def load_model(self, model_path: Path, **kwargs) -> None:
        """加载 MuseTalk 模型

        Args:
            model_path: MuseTalk 根目录
            **kwargs:
                version: "v15"（推荐）或 "v1"
                ffmpeg_path: FFmpeg 可执行文件路径
        """
        logger.info(f"Loading MuseTalk from {model_path}")
        self._model_path = model_path
        self._version = kwargs.get("version", "v15")
        self._ffmpeg_path = kwargs.get("ffmpeg_path", "ffmpeg")

        # 验证关键模型文件
        if self._version == "v15":
            unet_path = model_path / "models" / "musetalkV15" / "unet.pth"
            unet_config = model_path / "models" / "musetalkV15" / "musetalk.json"
        else:
            unet_path = model_path / "models" / "musetalk" / "pytorch_model.bin"
            unet_config = model_path / "models" / "musetalk" / "musetalk.json"

        missing = []
        if not unet_path.exists():
            missing.append(str(unet_path))
        if not unet_config.exists():
            missing.append(str(unet_config))

        # 检查依赖模型
        for dep in ["sd-vae", "whisper", "dwpose", "face-parse-bisent", "syncnet"]:
            dep_dir = model_path / "models" / dep
            if not dep_dir.exists():
                missing.append(str(dep_dir))

        if missing:
            raise FileNotFoundError(
                f"MuseTalk 模型文件缺失:\n" + "\n".join(f"  - {m}" for m in missing)
            )

        self._loaded = True
        logger.info(f"MuseTalk {self._version} loaded successfully")

    def generate(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        **kwargs,
    ) -> LipSyncResult:
        """生成唇形同步视频

        Args:
            video_path: 输入视频/图片路径
            audio_path: 输入音频路径
            output_path: 输出视频路径
            **kwargs:
                face_size: 人脸区域大小（默认 256）
                bbox_shift: 人脸区域偏移（影响生成质量，建议先用默认值测试）

        Returns:
            LipSyncResult: 生成结果
        """
        if not self._loaded:
            raise RuntimeError("模型未加载，请先调用 load_model()")

        logger.info(f"Generating lip sync: video={video_path}, audio={audio_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_dir = output_path.parent / "musetalk_result"
        result_dir.mkdir(parents=True, exist_ok=True)

        # 获取模型路径
        if self._version == "v15":
            unet_path = self._model_path / "models" / "musetalkV15" / "unet.pth"
            unet_config = self._model_path / "models" / "musetalkV15" / "musetalk.json"
        else:
            unet_path = self._model_path / "models" / "musetalk" / "pytorch_model.bin"
            unet_config = self._model_path / "models" / "musetalk" / "musetalk.json"

        # 生成推理配置文件
        inference_config = self._write_inference_config(video_path, audio_path, result_dir)

        # 构建推理命令
        cmd = [
            "python", "-m", "scripts.inference",
            "--inference_config", str(inference_config),
            "--result_dir", str(result_dir),
            "--unet_model_path", str(unet_path),
            "--unet_config", str(unet_config),
            "--version", self._version,
            "--ffmpeg_path", self._ffmpeg_path,
        ]

        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=str(self._model_path),
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            logger.error(f"MuseTalk stderr: {result.stderr}")
            raise RuntimeError(f"MuseTalk 推理失败: {result.stderr[-500:]}")

        # 找到输出视频
        result_videos = sorted(result_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not result_videos:
            raise RuntimeError("MuseTalk 未生成输出视频")

        # 移动到目标位置
        import shutil
        shutil.move(str(result_videos[0]), str(output_path))

        # 获取视频信息
        from ..utils.video import VideoUtils
        info = VideoUtils.get_info(output_path)

        logger.info(f"LipSync output: {output_path} ({info['duration']:.2f}s, {info['width']}x{info['height']}@{info['fps']}fps)")

        return LipSyncResult(
            video_path=output_path,
            fps=info["fps"],
            duration=info["duration"],
            resolution=(info["width"], info["height"]),
        )

    def _write_inference_config(self, video_path: Path, audio_path: Path, result_dir: Path) -> Path:
        """生成 MuseTalk 推理配置文件

        MuseTalk 使用 YAML 配置文件指定输入。
        """
        config = {
            "task_type": "avatar",
            "video_path": str(video_path),
            "audio_path": str(audio_path),
            "result_dir": str(result_dir),
        }

        config_path = self._model_path / "configs" / "inference" / "vtm_custom.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(yaml.dump(config, allow_unicode=True), encoding="utf-8")
        return config_path

    def is_loaded(self) -> bool:
        return self._loaded

    def unload(self) -> None:
        """卸载模型，释放显存"""
        self._model_path = None
        self._loaded = False
        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        logger.info("MuseTalk unloaded")
