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
                gpt_weights: GPT 模型权重文件名（可选，使用微调模型时指定）
                sovits_weights: SoVITS 模型权重文件名（可选）
        """
        logger.info(f"Loading GPT-SoVITS from {model_path}")

        try:
            from gpt_sovits import TTS, TTS_Config
        except ImportError:
            raise ImportError(
                "gpt-sovits-python 未安装。请运行: pip install gpt-sovits-python"
            )

        device = kwargs.get("device", "cuda")
        is_half = kwargs.get("is_half", device == "cuda")

        pretrained = model_path / "pretrained_models"

        # 支持自定义权重路径（用于微调模型）
        gpt_weights = kwargs.get("gpt_weights")
        sovits_weights = kwargs.get("sovits_weights")

        t2s_path = str(pretrained / (gpt_weights or "s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"))
        vits_path = str(pretrained / (sovits_weights or "s2G488k.pth"))

        soviets_configs = {
            "default": {
                "device": device,
                "is_half": is_half,
                "t2s_weights_path": t2s_path,
                "vits_weights_path": vits_path,
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
        """语音合成

        Args:
            text: 要合成的文本
            reference_audio: 参考音频路径（5秒以上效果更好）
            reference_text: 参考音频对应的文本（可选，提升效果）
            language: 文本语言 (zh/en/ja/all_zh/all_ja/yue/ko)
            **kwargs:
                output_dir: 输出目录
                top_k: 采样 top_k
                top_p: 采样 top_p
                temperature: 温度
                speed_factor: 语速因子
                seed: 随机种子（-1 为随机）
                media_type: 输出格式（wav/ogg/aac）

        Returns:
            TTSResult: 合成结果
        """
        if not self._loaded:
            raise RuntimeError("模型未加载，请先调用 load_model()")

        logger.info(f"Synthesizing: '{text[:50]}...' (lang={language})")

        output_dir = Path(kwargs.get("output_dir", "temp"))
        output_dir.mkdir(parents=True, exist_ok=True)
        media_type = kwargs.get("media_type", "wav")
        output_path = output_dir / f"tts_output.{media_type}"

        # 构建推理参数
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
            "seed": kwargs.get("seed", -1),
            "media_type": media_type,
            "streaming_mode": False,
            "text_split_method": "cut5",
            "batch_size": 1,
            "split_bucket": True,
            "fragment_interval": 0.3,
            "parallel_infer": True,
            "repetition_penalty": 1.35,
        }

        # 执行推理
        tts_generator = self._tts.run(params)
        sr, audio_data = next(tts_generator)

        # 保存输出
        import numpy as np
        if media_type == "wav":
            import scipy.io.wavfile
            scipy.io.wavfile.write(str(output_path), rate=sr, data=audio_data)
        else:
            import soundfile as sf
            sf.write(str(output_path), audio_data, sr)

        # 获取时长
        duration = len(audio_data) / sr

        logger.info(f"TTS output: {output_path} ({duration:.2f}s, {sr}Hz)")

        return TTSResult(
            audio_path=output_path,
            sample_rate=sr,
            duration=duration,
            text_processed=text,
        )

    def is_loaded(self) -> bool:
        return self._loaded

    def unload(self) -> None:
        """卸载模型，释放显存"""
        self._tts = None
        self._config = None
        self._loaded = False
        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        logger.info("GPT-SoVITS unloaded")
