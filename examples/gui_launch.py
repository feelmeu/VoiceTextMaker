"""VoiceTextMaker GUI 启动示例

用法:
    python -m examples.gui_launch

启动后浏览器会自动打开 Gradio 界面。
"""

from src.gui.app import create_app


def main():
    print("启动 VoiceTextMaker GUI...")
    print("浏览器将自动打开，如果没有请访问 http://127.0.0.1:7860")

    app = create_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
    )


if __name__ == "__main__":
    main()
