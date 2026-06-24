"""LipSync Provider 抽象基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LipSyncResult:
    """唇形同步推理结果"""
    video_path: Path          # 输出视频文件路径
    fps: int                  # 帧率
    duration: float           # 视频时长（秒）
    resolution: tuple[int, int]  # 分辨率 (width, height)


class LipSyncProvider(ABC):
    """唇形同步提供者抽象基类

    所有唇形驱动引擎（如 MuseTalk）都需要实现此接口。
    """

    @abstractmethod
    def load_model(self, model_path: Path, **kwargs) -> None:
        """加载模型

        Args:
            model_path: 模型文件/目录路径
            **kwargs: 额外配置参数
        """
        ...

    @abstractmethod
    def generate(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        **kwargs,
    ) -> LipSyncResult:
        """生成唇形同步视频

        Args:
            video_path: 输入视频/图片路径（人物素材）
            audio_path: 输入音频路径
            output_path: 输出视频路径
            **kwargs: 推理参数（face_size, bbox_shift 等）

        Returns:
            LipSyncResult: 生成结果
        """
        ...

    @abstractmethod
    def is_loaded(self) -> bool:
        """模型是否已加载"""
        ...

    def unload(self) -> None:
        """卸载模型，释放显存"""
        pass
