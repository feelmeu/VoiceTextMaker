"""配置管理模块"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class ModelConfig:
    """模型路径配置"""
    gpt_sovits_dir: Optional[Path] = None     # GPT-SoVITS 模型目录
    musetalk_dir: Optional[Path] = None       # MuseTalk 模型目录
    ffmpeg_path: Optional[Path] = None        # FFmpeg 路径


@dataclass
class AppConfig:
    """应用全局配置"""
    model: ModelConfig = field(default_factory=ModelConfig)
    output_dir: Path = Path("output")
    temp_dir: Path = Path("temp")
    log_level: str = "INFO"
    language: str = "zh"

    # GUI 配置
    window_width: int = 1200
    window_height: int = 800
    theme: str = "default"

    def save(self, path: Path) -> None:
        """保存配置到文件"""
        data = asdict(self)
        # Path 对象转字符串
        data = self._convert_paths(data)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        """从文件加载配置"""
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        """从字典创建配置"""
        # 处理嵌套的 ModelConfig
        if "model" in data and isinstance(data["model"], dict):
            for k, v in data["model"].items():
                if v is not None and (k.endswith("_dir") or k.endswith("_path")):
                    data["model"][k] = Path(v)
            data["model"] = ModelConfig(**data["model"])
        # 处理顶层 Path 字段
        for k in ["output_dir", "temp_dir"]:
            if k in data and data[k] is not None:
                data[k] = Path(data[k])
        return cls(**data)

    @staticmethod
    def _convert_paths(obj):
        """递归将 Path 转为字符串"""
        if isinstance(obj, dict):
            return {k: AppConfig._convert_paths(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [AppConfig._convert_paths(i) for i in obj]
        if isinstance(obj, Path):
            return str(obj)
        return obj
