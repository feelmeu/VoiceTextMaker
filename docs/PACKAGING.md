# Windows 打包指南

## 前提条件

- Windows 10/11 64位
- Python 3.10+
- NVIDIA GPU + CUDA 驱动（推荐，CPU 也可用但很慢）
- FFmpeg（需要单独下载）

## 打包步骤

### 1. 克隆项目

```powershell
git clone https://github.com/feelmeu/VoiceTextMaker.git
cd VoiceTextMaker
```

### 2. 创建虚拟环境

```powershell
conda create -n vtm python=3.10
conda activate vtm
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

### 4. 下载模型

#### GPT-SoVITS 模型

```powershell
# 方法 1: 使用整合包（推荐）
# 下载: https://huggingface.co/lj1995/GPT-SoVITS-windows-package

# 方法 2: 手动下载预训练模型
# 从 https://huggingface.co/lj1995/GPT-SoVITS 下载
# 放到 GPT-SoVITS/pretrained_models/ 目录
```

#### MuseTalk 模型

```powershell
# 克隆 MuseTalk
git clone https://github.com/TMElyralab/MuseTalk.git
cd MuseTalk

# 下载模型权重
download_weights.bat
# 或手动下载: https://huggingface.co/TMElyralab/MuseTalk
```

### 5. 运行打包脚本

```powershell
scripts\build_windows.bat
```

### 6. 测试打包结果

```powershell
cd dist\VoiceTextMaker
VoiceTextMaker.exe --help
```

## 打包后使用

### 启动 GUI

```powershell
VoiceTextMaker.exe gui
```

浏览器会自动打开 http://127.0.0.1:7860

### 命令行使用

```powershell
VoiceTextMaker.exe generate --text "你好世界" --reference-audio ref.wav --character-video char.mp4
```

## 模型文件管理

打包后的 exe **不包含**模型文件（体积太大）。用户需要：

1. 下载模型文件到本地目录
2. 在 GUI 的「模型设置」中指定模型目录路径
3. 首次使用时会自动下载部分依赖模型

## 常见问题

### Q: 打包后启动很慢？
A: 首次启动需要加载 PyTorch，约 10-30 秒。后续启动会快很多。

### Q: CUDA 不可用？
A: 确保安装了 NVIDIA 驱动和 CUDA Toolkit。可以在 cmd 中运行 `nvidia-smi` 检查。

### Q: 内存不足？
A: GPT-SoVITS + MuseTalk 至少需要 8GB 显存（GPU 模式）或 16GB 内存（CPU 模式）。

### Q: 如何使用微调模型？
A: 在 GUI 的模型设置中，指定 GPT-SoVITS 的微调权重文件路径。
