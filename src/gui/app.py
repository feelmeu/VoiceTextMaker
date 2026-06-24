"""Gradio GUI 应用"""

import time
from pathlib import Path
from typing import Optional

import gradio as gr

from ..core.config import AppConfig
from ..core.pipeline import Pipeline, PipelineConfig
from ..tts.gpt_sovits import GPTSoVITSProvider
from ..lipsync.musetalk import MuseTalkProvider
from ..utils.logger import get_logger

logger = get_logger("gui")


class VoiceTextMakerApp:
    """VoiceTextMaker GUI 应用"""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig()
        self.tts: Optional[GPTSoVITSProvider] = None
        self.lipsync: Optional[MuseTalkProvider] = None
        self.pipeline: Optional[Pipeline] = None
        self.history: list[dict] = []

    def load_models(
        self,
        gpt_sovits_dir: str,
        musetalk_dir: str,
        device: str = "cuda",
        ffmpeg_path: str = "ffmpeg",
    ) -> str:
        """加载 AI 模型"""
        try:
            # TTS
            self.tts = GPTSoVITSProvider()
            self.tts.load_model(
                Path(gpt_sovits_dir),
                device=device,
            )

            # LipSync
            self.lipsync = MuseTalkProvider()
            self.lipsync.load_model(
                Path(musetalk_dir),
                ffmpeg_path=ffmpeg_path,
            )

            # Pipeline
            pipeline_config = PipelineConfig(
                output_dir=self.config.output_dir,
                temp_dir=self.config.temp_dir,
            )
            self.pipeline = Pipeline(self.tts, self.lipsync, pipeline_config)

            return "✅ 模型加载成功！可以开始生成视频了。"

        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            return f"❌ 模型加载失败: {e}"

    def generate_video(
        self,
        text: str,
        reference_audio,
        character_video,
        language: str,
        speed_factor: float,
        temperature: float,
        progress=gr.Progress(),
    ):
        """生成视频"""
        if not self.pipeline:
            return None, "❌ 请先加载模型"

        if not text.strip():
            return None, "❌ 请输入文本"

        if reference_audio is None:
            return None, "❌ 请上传参考音频"

        if character_video is None:
            return None, "❌ 请上传人物视频/图片"

        try:
            # 保存上传的文件到临时目录
            ref_audio_path = Path(reference_audio)
            char_video_path = Path(character_video)

            # 更新 pipeline 配置
            self.pipeline.config.tts_language = language
            self.pipeline.config.tts_speed_factor = speed_factor
            self.pipeline.config.tts_temperature = temperature

            # 设置进度回调
            def on_progress(stage, current, total, desc):
                pct = current / total if total > 0 else 0
                if stage == "tts":
                    progress(pct * 0.4, desc=f"[语音合成] {desc}")
                else:
                    progress(0.4 + pct * 0.6, desc=f"[唇形驱动] {desc}")

            self.pipeline.set_progress_callback(on_progress)

            # 执行
            result = self.pipeline.run(
                text=text,
                reference_audio=ref_audio_path,
                character_video=char_video_path,
            )

            # 保存到历史记录
            self.history.append({
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "text": text[:100],
                "output": str(result.final_video),
                "duration": f"{result.total_duration:.1f}s",
            })

            return str(result.final_video), f"✅ 生成完成！耗时 {result.total_duration:.1f}s"

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None, f"❌ 生成失败: {e}"

    def get_history_text(self) -> str:
        """获取历史记录文本"""
        if not self.history:
            return "暂无历史记录"
        lines = []
        for i, h in enumerate(reversed(self.history), 1):
            lines.append(f"{i}. [{h['time']}] {h['text']} ({h['duration']})")
        return "\n".join(lines)

    def build_ui(self) -> gr.Blocks:
        """构建 Gradio UI"""
        with gr.Blocks(
            title="VoiceTextMaker",
            theme=gr.themes.Soft(),
            css="""
            .main-title { text-align: center; margin-bottom: 20px; }
            .status-box { padding: 10px; border-radius: 5px; }
            """,
        ) as app:
            gr.Markdown(
                "# 🎬 VoiceTextMaker\n### AI 语音克隆 + 唇形同步视频生成",
                elem_classes=["main-title"],
            )

            with gr.Tabs():
                # Tab 1: 生成视频
                with gr.TabItem("🎬 生成视频"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            text_input = gr.Textbox(
                                label="📝 要朗读的文本",
                                placeholder="输入你想让角色说的内容...",
                                lines=5,
                            )
                            reference_audio = gr.Audio(
                                label="🎤 参考音频（用于克隆音色，≥5秒）",
                                type="filepath",
                            )
                            character_video = gr.Video(
                                label="👤 人物视频/图片",
                            )

                        with gr.Column(scale=1):
                            with gr.Accordion("⚙️ 参数设置", open=False):
                                language = gr.Dropdown(
                                    label="语言",
                                    choices=[
                                        ("中文", "zh"),
                                        ("英文", "en"),
                                        ("日文", "ja"),
                                        ("中英混合", "zh_en"),
                                    ],
                                    value="zh",
                                )
                                speed_factor = gr.Slider(
                                    label="语速",
                                    minimum=0.5,
                                    maximum=2.0,
                                    value=1.0,
                                    step=0.1,
                                )
                                temperature = gr.Slider(
                                    label="温度（越高越随机）",
                                    minimum=0.1,
                                    maximum=2.0,
                                    value=1.0,
                                    step=0.1,
                                )

                            generate_btn = gr.Button(
                                "🚀 开始生成",
                                variant="primary",
                                size="lg",
                            )

                            status_text = gr.Textbox(
                                label="状态",
                                value="请先在「模型设置」中加载模型",
                                interactive=False,
                            )

                            output_video = gr.Video(
                                label="📺 生成结果",
                            )

                # Tab 2: 模型设置
                with gr.TabItem("⚙️ 模型设置"):
                    gr.Markdown("### 加载 AI 模型")
                    gr.Markdown("首次使用需要指定模型目录路径。")

                    with gr.Row():
                        gpt_sovits_dir = gr.Textbox(
                            label="GPT-SoVITS 目录",
                            placeholder="包含 pretrained_models/ 的目录路径",
                        )
                        musetalk_dir = gr.Textbox(
                            label="MuseTalk 目录",
                            placeholder="包含 models/ 的目录路径",
                        )

                    with gr.Row():
                        device = gr.Dropdown(
                            label="推理设备",
                            choices=[("CUDA (GPU)", "cuda"), ("CPU", "cpu")],
                            value="cuda",
                        )
                        ffmpeg_path = gr.Textbox(
                            label="FFmpeg 路径",
                            value="ffmpeg",
                        )

                    load_btn = gr.Button("📦 加载模型", variant="secondary")
                    load_status = gr.Textbox(label="加载状态", interactive=False)

                    load_btn.click(
                        fn=self.load_models,
                        inputs=[gpt_sovits_dir, musetalk_dir, device, ffmpeg_path],
                        outputs=load_status,
                    )

                # Tab 3: 历史记录
                with gr.TabItem("📋 历史记录"):
                    history_text = gr.Textbox(
                        label="生成历史",
                        value="暂无历史记录",
                        lines=15,
                        interactive=False,
                    )
                    refresh_btn = gr.Button("🔄 刷新")
                    refresh_btn.click(
                        fn=self.get_history_text,
                        outputs=history_text,
                    )

            # 绑定生成按钮
            generate_btn.click(
                fn=self.generate_video,
                inputs=[
                    text_input,
                    reference_audio,
                    character_video,
                    language,
                    speed_factor,
                    temperature,
                ],
                outputs=[output_video, status_text],
            )

        return app


def create_app(config: Optional[AppConfig] = None) -> gr.Blocks:
    """创建 Gradio 应用实例

    Args:
        config: 应用配置

    Returns:
        gr.Blocks: Gradio 应用
    """
    app = VoiceTextMakerApp(config)
    return app.build_ui()
