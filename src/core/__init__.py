"""核心抽象层"""

from .tts_provider import TTSProvider, TTSResult
from .lipsync_provider import LipSyncProvider, LipSyncResult
from .pipeline import Pipeline, PipelineConfig, PipelineResult

__all__ = [
    "TTSProvider", "TTSResult",
    "LipSyncProvider", "LipSyncResult",
    "Pipeline", "PipelineConfig", "PipelineResult",
]
