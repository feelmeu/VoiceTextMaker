"""端到端流水线集成测试"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

from src.core.tts_provider import TTSProvider, TTSResult
from src.core.lipsync_provider import LipSyncProvider, LipSyncResult
from src.core.pipeline import Pipeline, PipelineConfig


class MockTTSProvider(TTSProvider):
    """Mock TTS Provider 用于测试"""

    def __init__(self):
        self._loaded = False

    def load_model(self, model_path, **kwargs):
        self._loaded = True

    def synthesize(self, text, reference_audio, reference_text=None, language="zh", **kwargs):
        output_dir = Path(kwargs.get("output_dir", "temp"))
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "tts_output.wav"
        output_path.write_bytes(b"RIFF" + b"\x00" * 100)  # dummy wav
        return TTSResult(
            audio_path=output_path,
            sample_rate=32000,
            duration=5.0,
            text_processed=text,
        )

    def is_loaded(self):
        return self._loaded


class MockLipSyncProvider(LipSyncProvider):
    """Mock LipSync Provider 用于测试"""

    def __init__(self):
        self._loaded = False

    def load_model(self, model_path, **kwargs):
        self._loaded = True

    def generate(self, video_path, audio_path, output_path, **kwargs):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"\x00" * 100)  # dummy mp4
        return LipSyncResult(
            video_path=output_path,
            fps=25,
            duration=5.0,
            resolution=(512, 512),
        )

    def is_loaded(self):
        return self._loaded


class TestPipelineIntegration:
    """端到端流水线测试"""

    def test_full_pipeline(self, tmp_path):
        """测试完整流水线流程"""
        tts = MockTTSProvider()
        lipsync = MockLipSyncProvider()
        tts.load_model(tmp_path)
        lipsync.load_model(tmp_path)

        config = PipelineConfig(
            output_dir=tmp_path / "output",
            temp_dir=tmp_path / "temp",
            cleanup_temp=False,
        )
        pipeline = Pipeline(tts, lipsync, config)

        # 创建测试输入文件
        ref_audio = tmp_path / "ref.wav"
        ref_audio.write_bytes(b"RIFF" + b"\x00" * 100)
        char_video = tmp_path / "char.mp4"
        char_video.write_bytes(b"\x00" * 100)

        result = pipeline.run(
            text="你好世界",
            reference_audio=ref_audio,
            character_video=char_video,
        )

        assert result.tts_result.audio_path.exists()
        assert result.lipsync_result.video_path.exists()
        assert result.final_video.exists()
        assert result.total_duration > 0

    def test_progress_callback(self, tmp_path):
        """测试进度回调"""
        tts = MockTTSProvider()
        lipsync = MockLipSyncProvider()
        tts.load_model(tmp_path)
        lipsync.load_model(tmp_path)

        pipeline = Pipeline(tts, lipsync, PipelineConfig(
            output_dir=tmp_path / "output",
            temp_dir=tmp_path / "temp",
        ))

        callback = MagicMock()
        pipeline.set_progress_callback(callback)

        ref_audio = tmp_path / "ref.wav"
        ref_audio.write_bytes(b"RIFF" + b"\x00" * 100)
        char_video = tmp_path / "char.mp4"
        char_video.write_bytes(b"\x00" * 100)

        pipeline.run(
            text="测试",
            reference_audio=ref_audio,
            character_video=char_video,
        )

        # 应该有 4 次回调：tts 0/100, tts 100/100, lipsync 0/100, lipsync 100/100
        assert callback.call_count == 4

    def test_cleanup_temp(self, tmp_path):
        """测试临时文件清理"""
        tts = MockTTSProvider()
        lipsync = MockLipSyncProvider()
        tts.load_model(tmp_path)
        lipsync.load_model(tmp_path)

        temp_dir = tmp_path / "temp"
        config = PipelineConfig(
            output_dir=tmp_path / "output",
            temp_dir=temp_dir,
            cleanup_temp=True,
        )
        pipeline = Pipeline(tts, lipsync, config)

        ref_audio = tmp_path / "ref.wav"
        ref_audio.write_bytes(b"RIFF" + b"\x00" * 100)
        char_video = tmp_path / "char.mp4"
        char_video.write_bytes(b"\x00" * 100)

        pipeline.run(
            text="测试清理",
            reference_audio=ref_audio,
            character_video=char_video,
        )

        # 临时目录应该被清理
        assert not temp_dir.exists()

    def test_custom_output_path(self, tmp_path):
        """测试自定义输出路径"""
        tts = MockTTSProvider()
        lipsync = MockLipSyncProvider()
        tts.load_model(tmp_path)
        lipsync.load_model(tmp_path)

        pipeline = Pipeline(tts, lipsync, PipelineConfig(
            output_dir=tmp_path / "output",
            temp_dir=tmp_path / "temp",
        ))

        ref_audio = tmp_path / "ref.wav"
        ref_audio.write_bytes(b"RIFF" + b"\x00" * 100)
        char_video = tmp_path / "char.mp4"
        char_video.write_bytes(b"\x00" * 100)

        custom_output = tmp_path / "custom" / "result.mp4"
        result = pipeline.run(
            text="自定义路径",
            reference_audio=ref_audio,
            character_video=char_video,
            output_path=custom_output,
        )

        assert result.final_video == custom_output
        assert custom_output.exists()
