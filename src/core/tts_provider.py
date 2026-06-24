"""TTS Provider 抽象基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TTSResult:
    """TTS 推理结果"""
    audio_path: Path          # 输出音频文件路径
    sample_rate: int          # 采样率
    duration: float           # 音频时长（秒）
    text_processed: str       # 实际处理的文本


class TTSProvider(ABC):
    """TTS 语音合成提供者抽象基类

    所有 TTS 引擎（如 GPT-SoVITS）都需要实现此接口。
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
    def synthesize(
        self,
        text: str,
        reference_audio: Path,
        reference_text: Optional[str] = None,
        language: str = "zh",
        **kwargs,
    ) -> TTSResult:
        """语音合成

        Args:
            text: 要合成的文本
            reference_audio: 参考音频路径（用于克隆音色）
            reference_text: 参考音频对应的文本（可选，提升效果）
            language: 文本语言 (zh/en/ja/ko)
            **kwargs: 推理参数（temperature, top_k, speed_factor 等）

        Returns:
            TTSResult: 合成结果
        """
        ...

    @abstractmethod
    def is_loaded(self) -> bool:
        """模型是否已加载"""
        ...

    def unload(self) -> None:
        """卸载模型，释放显存"""
        pass
