"""VoiceTextMaker 基本使用示例

用法:
    python -m examples.basic_usage

前提:
    1. 已安装所有依赖
    2. 已下载 GPT-SoVITS 和 MuseTalk 模型
    3. 准备好参考音频和人物视频
"""

from pathlib import Path
from src.core.pipeline import Pipeline, PipelineConfig
from src.tts.gpt_sovits import GPTSoVITSProvider
from src.lipsync.musetalk import MuseTalkProvider


def main():
    # ===== 配置 =====
    GPT_SOVITS_DIR = Path("path/to/GPT-SoVITS")  # 替换为实际路径
    MUSETALK_DIR = Path("path/to/MuseTalk")        # 替换为实际路径
    REFERENCE_AUDIO = Path("path/to/reference.wav") # 参考音频（≥5秒）
    CHARACTER_VIDEO = Path("path/to/character.mp4") # 人物视频
    OUTPUT_VIDEO = Path("output/result.mp4")        # 输出路径

    TEXT = "你好，我是 VoiceTextMaker，今天我来给大家演示一下这个神奇的功能。"

    # ===== 初始化 =====
    print("加载模型...")
    tts = GPTSoVITSProvider()
    tts.load_model(GPT_SOVITS_DIR, device="cuda")

    lipsync = MuseTalkProvider()
    lipsync.load_model(MUSETALK_DIR)

    # ===== 创建流水线 =====
    config = PipelineConfig(
        tts_language="zh",
        tts_speed_factor=1.0,
        output_dir=Path("output"),
        temp_dir=Path("temp"),
    )
    pipeline = Pipeline(tts, lipsync, config)

    # 设置进度回调
    def on_progress(stage, current, total, desc):
        pct = int(current / total * 100) if total > 0 else 0
        print(f"[{stage.upper()}] {desc} ({pct}%)")

    pipeline.set_progress_callback(on_progress)

    # ===== 生成 =====
    print(f"\n开始生成: '{TEXT[:50]}...'")
    result = pipeline.run(
        text=TEXT,
        reference_audio=REFERENCE_AUDIO,
        character_video=CHARACTER_VIDEO,
        output_path=OUTPUT_VIDEO,
    )

    print(f"\n✅ 生成完成!")
    print(f"   输出: {result.final_video}")
    print(f"   语音时长: {result.tts_result.duration:.1f}s")
    print(f"   视频时长: {result.lipsync_result.duration:.1f}s")
    print(f"   总耗时: {result.total_duration:.1f}s")


if __name__ == "__main__":
    main()
