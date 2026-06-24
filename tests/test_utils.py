"""工具模块单元测试"""

import pytest
from pathlib import Path

from src.utils.logger import get_logger


class TestLogger:
    def test_get_logger(self):
        logger = get_logger("test")
        assert logger.name == "test"

    def test_logger_level(self):
        logger = get_logger("test_debug", level="DEBUG")
        assert logger.level == 10  # DEBUG = 10

    def test_logger_singleton(self):
        logger1 = get_logger("test_same")
        logger2 = get_logger("test_same")
        assert logger1 is logger2
