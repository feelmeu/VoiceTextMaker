"""VoiceTextMaker 主入口"""

import argparse
import sys
from pathlib import Path

from .core.config import AppConfig
from .core.pipeline import Pipeline, PipelineConfig
from .utils.logger import get_logger

logger = get_logger("main")


def create_pipeline(config: AppConfig) -> Pipeline:
    """根据配置创建流水线实例"""
    from .tts.gpt_sovits import GPTSoVITSProvider
    from .lipsync.musetalk import MuseTalkProvider

    tts = GPTSoVITSProvider()
    lipsync = MuseTalkProvider()

    pipeline_config = PipelineConfig(
        output_dir=config.output_dir,
        temp_dir=config.temp_dir,
    )

    pipeline = Pipeline(tts, lipsync, pipeline_config)

    # 设置进度回调
    def on_progress(stage, current, total, desc):
        pct = int(current / total * 100) if total > 0 else 0
        print(f"\r[{stage.upper()}] {desc} ({pct}%)", end="", flush=True)
        if current == total:
            print()

    pipeline.set_progress_callback(on_progress)
    return pipeline


def run_cli(args):
    """命令行模式运行"""
    config = AppConfig.load(Path(args.config) if args.config else AppConfig())

    logger.info("VoiceTextMaker starting...")

    pipeline = create_pipeline(config)

    # 加载模型
    logger.info("Loading models...")
    pipeline.tts.load_model(
        config.model.gpt_sovits_dir,
        device=args.device,
    )
    pipeline.lipsync.load_model(
        config.model.musetalk_dir,
        ffmpeg_path=str(config.model.ffmpeg_path) if config.model.ffmpeg_path else "ffmpeg",
    )

    # 执行
    result = pipeline.run(
        text=args.text,
        reference_audio=Path(args.reference_audio),
        character_video=Path(args.character_video),
        output_path=Path(args.output) if args.output else None,
    )

    logger.info(f"Done! Output: {result.final_video}")
    logger.info(f"Total time: {result.total_duration:.1f}s")


def run_gui(args):
    """GUI 模式运行"""
    from .gui.app import create_app
    config = AppConfig.load(Path(args.config) if args.config else AppConfig())
    app = create_app(config)
    app.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        inbrowser=True,
    )


def main():
    parser = argparse.ArgumentParser(description="VoiceTextMaker - AI 语音克隆 + 唇形同步视频生成")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"], help="推理设备")

    subparsers = parser.add_subparsers(dest="command")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="命令行生成视频")
    gen_parser.add_argument("--text", type=str, required=True, help="要朗读的文本")
    gen_parser.add_argument("--reference-audio", type=str, required=True, help="参考音频路径（用于语音克隆）")
    gen_parser.add_argument("--character-video", type=str, required=True, help="人物视频/图片路径")
    gen_parser.add_argument("--output", type=str, help="输出视频路径")

    # gui 子命令
    gui_parser = subparsers.add_parser("gui", help="启动图形界面")
    gui_parser.add_argument("--host", type=str, default="127.0.0.1", help="服务器地址")
    gui_parser.add_argument("--port", type=int, default=7860, help="服务器端口")
    gui_parser.add_argument("--share", action="store_true", help="创建公网链接")

    args = parser.parse_args()

    if args.command == "generate":
        run_cli(args)
    elif args.command == "gui":
        run_gui(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
