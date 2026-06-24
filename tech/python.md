# Python 技术栈约定

## 环境

- Python 3.10+（与 PyTorch CUDA 兼容性最佳）
- 虚拟环境：conda 或 venv
- 包管理：pip + requirements.txt

## 核心依赖

- PyTorch 2.x + CUDA 12.x（GPU 加速）
- GPT-SoVITS（语音克隆）
- MuseTalk（唇形驱动）
- FFmpeg（音视频处理）
- OpenCV（图像处理）
- Gradio / PyQt（GUI，待 ADR 决策）

## 代码规范

- 遵循 PEP 8
- 类型注解：使用 type hints
- 文档字符串：Google 风格
- 测试框架：pytest

## 打包

- PyInstaller 打包为 Windows 可执行程序
- 模型文件不打包进 exe，首次运行时下载或由用户指定路径
