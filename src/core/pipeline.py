"""核心流水线：文本 → 语音 → 唇形同步视频"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable

from .tts_provider import TTSProvider, TTSResult
from .lipsync_provider import LipSyncProvider, LipSyncResult


@dataclass
class PipelineConfig:
    """流水线配置"""
    # TTS 参数
    tts_language: str = "zh"
    tts_reference_text: Optional[str] = None
    tts_temperature: float = 1.0
    tts_top_k: int = 5
    tts_speed_factor: float = 1.0

    # LipSync 参数
    lipsync_face_size: int = 256
    lipsync_bbox_shift: int = 0

    # 通用参数
    output_dir: Path = Path("output")
    temp_dir: Path = Path("temp")
    cleanup_temp: bool = True


@dataclass
class PipelineResult:
    """流水线执行结果"""
    tts_result: TTSResult
    lipsync_result: LipSyncResult
    final_video: Path         # 最终输出视频路径
    total_duration: float     # 总耗时（秒）


# 进度回调类型：(阶段名, 当前进度, 总进度, 描述)
ProgressCallback = Callable[[str, int, int, str], None]


class Pipeline:
    """核心流水线

    将 TTS 和 LipSync 串联为完整的视频生成流程。
    """

    def __init__(
        self,
        tts_provider: TTSProvider,
        lipsync_provider: LipSyncProvider,
        config: Optional[PipelineConfig] = None,
    ):
        self.tts = tts_provider
        self.lipsync = lipsync_provider
        self.config = config or PipelineConfig()
        self._progress_callback: Optional[ProgressCallback] = None

    def set_progress_callback(self, callback: ProgressCallback) -> None:
        """设置进度回调"""
        self._progress_callback = callback

    def _report_progress(self, stage: str, current: int, total: int, desc: str) -> None:
        """报告进度"""
        if self._progress_callback:
            self._progress_callback(stage, current, total, desc)

    def run(
        self,
        text: str,
        reference_audio: Path,
        character_video: Path,
        output_path: Optional[Path] = None,
    ) -> PipelineResult:
        """执行完整流水线

        Args:
            text: 要朗读的文本
            reference_audio: 参考音频路径（用于语音克隆）
            character_video: 人物视频/图片路径
            output_path: 输出视频路径（可选，默认自动生成）

        Returns:
            PipelineResult: 执行结果
        """
        import time
        start_time = time.time()

        # 准备目录
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.temp_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: TTS 语音合成
        self._report_progress("tts", 0, 100, "正在合成语音...")
        tts_result = self.tts.synthesize(
            text=text,
            reference_audio=reference_audio,
            reference_text=self.config.tts_reference_text,
            language=self.config.tts_language,
            temperature=self.config.tts_temperature,
            top_k=self.config.tts_top_k,
            speed_factor=self.config.tts_speed_factor,
        )
        self._report_progress("tts", 100, 100, "语音合成完成")

        # Step 2: LipSync 唇形驱动
        self._report_progress("lipsync", 0, 100, "正在生成唇形同步视频...")
        if output_path is None:
            output_path = self.config.output_dir / "result.mp4"

        lipsync_result = self.lipsync.generate(
            video_path=character_video,
            audio_path=tts_result.audio_path,
            output_path=output_path,
            face_size=self.config.lipsync_face_size,
            bbox_shift=self.config.lipsync_bbox_shift,
        )
        self._report_progress("lipsync", 100, 100, "唇形同步完成")

        # 清理临时文件
        if self.config.cleanup_temp:
            self._cleanup_temp()

        total_time = time.time() - start_time

        return PipelineResult(
            tts_result=tts_result,
            lipsync_result=lipsync_result,
            final_video=output_path,
            total_duration=total_time,
        )

    def _cleanup_temp(self) -> None:
        """清理临时文件"""
        import shutil
        if self.config.temp_dir.exists():
            shutil.rmtree(self.config.temp_dir, ignore_errors=True)
