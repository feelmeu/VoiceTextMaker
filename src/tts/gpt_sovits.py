"""GPT-SoVITS TTS Provider 实现"""

from pathlib import Path
from typing import Optional

from ..core.tts_provider import TTSProvider, TTSResult
from ..utils.logger import get_logger

logger = get_logger("gpt_sovits")


class GPTSoVITSProvider(TTSProvider):
    """GPT-SoVITS 语音合成提供者

    基于 gpt-sovits-python 包实现。
    参考: https://pypi.org/project/gpt-sovits-python/
    """

    def __init__(self):
        self._tts = None
        self._config = None
        self._loaded = False

    def load_model(self, model_path: Path, **kwargs) -> None:
        """加载 GPT-SoVITS 模型

        Args:
            model_path: GPT-SoVITS 根目录（包含 pretrained_models/）
            **kwargs:
                device: "cuda" / "cpu"
                is_half: 是否使用半精度
        """
        logger.info(f"Loading GPT-SoVITS from {model_path}")

        try:
            from gpt_sovits import TTS, TTS_Config
        except ImportError:
            raise ImportError(
                "gpt-sovits-python 未安装。请运行: pip install gpt-sovits-python"
            )

        device = kwargs.get("device", "cuda")
        is_half = kwargs.get("is_half", True)

        pretrained = model_path / "pretrained_models"
        soviets_configs = {
            "default": {
                "device": device,
                "is_half": is_half,
                "t2s_weights_path": str(pretrained / "s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"),
                "vits_weights_path": str(pretrained / "s2G488k.pth"),
                "cnhuhbert_base_path": str(pretrained / "chinese-hubert-base"),
                "bert_base_path": str(pretrained / "chinese-roberta-wwm-ext-large"),
            }
        }

        self._config = TTS_Config(soviets_configs)
        self._tts = TTS(self._config)
        self._loaded = True
        logger.info("GPT-SoVITS loaded successfully")

    def synthesize(
        self,
        text: str,
        reference_audio: Path,
        reference_text: Optional[str] = None,
        language: str = "zh",
        **kwargs,
    ) -> TTSResult:
        """语音合成"""
        if not self._loaded:
            raise RuntimeError("模型未加载，请先调用 load_model()")

        logger.info(f"Synthesizing: '{text[:50]}...' (lang={language})")

        output_dir = Path(kwargs.get("output_dir", "temp"))
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "tts_output.wav"

        # 调用 gpt-sovits-python 推理
        params = {
            "text": text,
            "text_lang": language,
            "ref_audio_path": str(reference_audio),
            "prompt_text": reference_text or "",
            "prompt_lang": language,
            "top_k": kwargs.get("top_k", 5),
            "top_p": kwargs.get("top_p", 1.0),
            "temperature": kwargs.get("temperature", 1.0),
            "speed_factor": kwargs.get("speed_factor", 1.0),
        }

        result = self._tts.synthesize(**params)

        # 保存输出
        if hasattr(result, "save"):
            result.save(str(output_path))
        elif hasattr(result, "audio"):
            import torchaudio
            torchaudio.save(str(output_path), result.audio, result.sample_rate)

        # 获取时长
        from ..utils.audio import AudioUtils
        duration = AudioUtils.get_duration(output_path)

        return TTSResult(
            audio_path=output_path,
            sample_rate=getattr(result, "sample_rate", 32000),
            duration=duration,
            text_processed=text,
        )

    def is_loaded(self) -> bool:
        return self._loaded

    def unload(self) -> None:
        self._tts = None
        self._config = None
        self._loaded = False
        logger.info("GPT-SoVITS unloaded")
