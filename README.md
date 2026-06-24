# VoiceTextMaker

AI 驱动的语音克隆 + 唇形同步视频生成工具。

## 功能

- 从照片/视频获取人物形象
- 从录音克隆语音
- 输入文本 → 自动生成指定人物"说话"的视频（语音 + 唇形同步）
- 完整 GUI 界面，支持参数调节、历史记录、视频预览

## 技术路线

| 模块 | 方案 | 说明 |
|---|---|---|
| 语音克隆 TTS | GPT-SoVITS | 5秒音频即可克隆，中文效果最佳 |
| 唇形驱动 | MuseTalk | 腾讯开源，实时高质量唇形同步 |
| GUI | 待定 (ADR 决策) | PyQt / Gradio / Streamlit |
| 打包 | PyInstaller | Windows 可执行程序 |

## 目录结构

```
VoiceTextMaker/
├── .scratch/
│   ├── templates/          ← 模板
│   └── issues/             ← 任务追踪
├── docs/
│   └── adr/                ← 架构决策记录
├── tech/                   ← 技术栈术语
├── src/                    ← 源代码
├── CONTEXT.md              ← 项目术语表
└── workflow.md             ← 工作流程
```

## 使用方式

待开发完成后补充。
