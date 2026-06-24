# Windows 环境搭建指南

> 本文档记录了在 Windows 上从零搭建 VoiceTextMaker 开发环境的完整过程及常见问题解决方案。
> 更新日期：2026-06-24

---

## 1. 安装 Miniconda

项目需要 Python 3.10 环境，推荐使用 Miniconda 管理。

### 下载安装

1. 下载：https://docs.conda.io/en/latest/miniconda.html
   - 选择 **Windows 64-bit** 安装包
2. 安装时勾选 **"Add Miniconda to my PATH environment variable"**

### 常见问题：conda 命令不可用

**症状：** PowerShell 提示 `无法将"conda"项识别为 cmdlet、函数、脚本文件或可运行程序的名称`

**原因：** PowerShell 执行策略禁止运行脚本

**解决：**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
执行后**重启 PowerShell**。

---

## 2. 创建 Python 环境

```powershell
conda create -n vtm python=3.10
conda activate vtm
```

### 常见问题：conda activate 无反应 / Python 版本仍为系统版本

**症状：** 执行 `conda activate vtm` 后 `python --version` 仍显示 3.13.x

**原因：** PowerShell 执行策略阻止了 conda 的激活脚本

**解决：**
1. 执行 `conda init powershell`
2. 确保已执行 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. **重启 PowerShell** 后再 `conda activate vtm`

**验证：**
```powershell
python --version
# 应显示 Python 3.10.x
```

---

## 3. 安装依赖

### 基础依赖

```powershell
pip install gpt-sovits-python --no-deps
pip install torch>=2.0.0 torchaudio>=2.0.0 typing-extensions>=4.10.0
pip install cn2an einops ffmpeg-python g2p-en jieba-fast LangSegment pyopenjtalk pypinyin pytorch-lightning typeguard==4.2.0
pip install opencv-python librosa soundfile scipy Pillow gradio pytest pytest-cov
```

### 常见问题：typing-extensions 版本冲突

**症状：** `ERROR: Cannot install ... because these package versions have conflicting dependencies`

**原因：** `gpt-sovits-python` 锁定 `typing-extensions==4.9.0`，但 `torch>=2.0` 要求 `>=4.10.0`

**解决：** 使用 `--no-deps` 安装 `gpt-sovits-python`，然后手动安装其他依赖。`typing-extensions` 使用新版本即可，运行时一般不会有问题。

### 常见问题：numpy 构建失败

**症状：** `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'`

**原因：** 在错误的 Python 版本（如 3.13）下安装了旧版 numpy

**解决：** 确保 conda 环境已激活（`python --version` 应显示 3.10），然后 `pip install numpy --upgrade`

---

## 4. 下载模型

### HuggingFace 下载失败

**症状：** `Error: Local entry not found. Distant resource does not seem to be on huggingface.co`

**原因：** 国内网络无法直接访问 HuggingFace

**解决：** 设置镜像环境变量

```powershell
# 临时设置（当前会话有效）
$env:HF_ENDPOINT = "https://hf-mirror.com"

# 永久设置（重启后仍有效）
setx HF_ENDPOINT "https://hf-mirror.com"
```

设置后**重启 PowerShell** 再执行下载。

### MuseTalk 模型

项目需要以下模型文件：
```
musetalk_root/
├── models/
│   ├── musetalkV15/
│   │   ├── unet.pth
│   │   └── musetalk.json
│   ├── sd-vae/
│   ├── whisper/
│   ├── dwpose/
│   ├── face-parse-bisent/
│   └── syncnet/
```

可从以下地址下载：
- 官方：https://huggingface.co/TMElyralab/MuseTalk
- 镜像：https://hf-mirror.com/TMElyralab/MuseTalk

---

## 5. 运行项目

```powershell
conda activate vtm
cd C:\path\to\VoiceTextMaker
python -m src.main
```

### 常见问题：相对导入错误

**症状：** `ImportError: attempted relative import with no known parent package`

**原因：** 直接运行 `python src\main.py` 不识别包结构

**解决：** 使用 `python -m src.main` 代替 `python src\main.py`

### 启动 GUI

```powershell
python -m src.main gui
```

### 命令行生成

```powershell
python -m src.main generate --text "你好世界" --reference-audio ref.wav --character-video face.mp4
```

---

## 快速检查清单

| 检查项 | 命令 | 期望结果 |
|--------|------|----------|
| conda 可用 | `conda --version` | 显示版本号 |
| 环境已激活 | `python --version` | `Python 3.10.x` |
| torch 已安装 | `python -c "import torch; print(torch.__version__)"` | 显示版本号 |
| CUDA 可用 | `python -c "import torch; print(torch.cuda.is_available())"` | `True` |
| 模型文件存在 | 检查 musetalk 目录结构 | 文件完整 |
