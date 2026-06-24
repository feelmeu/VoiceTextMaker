"""核心抽象层单元测试"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.core.tts_provider import TTSProvider, TTSResult
from src.core.lipsync_provider import LipSyncProvider, LipSyncResult
from src.core.pipeline import Pipeline, PipelineConfig, PipelineResult
from src.core.config import AppConfig, ModelConfig


# ========== TTS Provider 测试 ==========

class TestTTSResult:
    def test_creation(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.touch()
        result = TTSResult(
            audio_path=audio,
            sample_rate=32000,
            duration=5.0,
            text_processed="你好世界",
        )
        assert result.audio_path == audio
        assert result.sample_rate == 32000
        assert result.duration == 5.0


class TestTTSProvider:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            TTSProvider()


# ========== LipSync Provider 测试 ==========

class TestLipSyncResult:
    def test_creation(self, tmp_path):
        video = tmp_path / "test.mp4"
        video.touch()
        result = LipSyncResult(
            video_path=video,
            fps=25,
            duration=10.0,
            resolution=(512, 512),
        )
        assert result.fps == 25
        assert result.resolution == (512, 512)


class TestLipSyncProvider:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            LipSyncProvider()


# ========== Pipeline 测试 ==========

class TestPipelineConfig:
    def test_default_config(self):
        config = PipelineConfig()
        assert config.tts_language == "zh"
        assert config.tts_temperature == 1.0
        assert config.cleanup_temp is True

    def test_custom_config(self):
        config = PipelineConfig(tts_language="en", tts_speed_factor=1.5)
        assert config.tts_language == "en"
        assert config.tts_speed_factor == 1.5


class TestPipeline:
    def test_progress_callback(self):
        """测试进度回调机制"""
        mock_tts = MagicMock(spec=TTSProvider)
        mock_lipsync = MagicMock(spec=LipSyncProvider)
        pipeline = Pipeline(mock_tts, mock_lipsync)

        callback = MagicMock()
        pipeline.set_progress_callback(callback)
        pipeline._report_progress("test", 50, 100, "testing")

        callback.assert_called_once_with("test", 50, 100, "testing")


# ========== Config 测试 ==========

class TestAppConfig:
    def test_default_config(self):
        config = AppConfig()
        assert config.log_level == "INFO"
        assert config.language == "zh"

    def test_save_and_load(self, tmp_path):
        config_path = tmp_path / "config.json"
        config = AppConfig(log_level="DEBUG")
        config.save(config_path)

        loaded = AppConfig.load(config_path)
        assert loaded.log_level == "DEBUG"

    def test_load_nonexistent(self, tmp_path):
        config = AppConfig.load(tmp_path / "nonexistent.json")
        assert config.log_level == "INFO"  # 默认值


class TestModelConfig:
    def test_default(self):
        config = ModelConfig()
        assert config.gpt_sovits_dir is None
        assert config.musetalk_dir is None
