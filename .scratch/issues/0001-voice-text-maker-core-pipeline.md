---
role: ready-for-work
title: VoiceTextMaker 核心流水线 — 语音克隆 + 唇形同步视频生成
created_at: 2026-06-24
importance: high
---

# 0001 — VoiceTextMaker 核心流水线

## 目标

构建一个完整的 AI 流水线：从人物照片/视频获取形象 → 从录音克隆语音 → 输入文本自动生成指定人物"说话"的视频（语音 + 唇形同步），附带完整 GUI 和 Windows 可执行打包。

## In Scope

- [ ] 语音克隆模块：输入参考音频 + 文本 → 输出克隆语音
- [ ] 唇形驱动模块：输入音频 + 人物视频/图片 → 输出唇形同步视频
- [ ] 完整 GUI 界面：文件选择、参数调节、进度显示、视频预览
- [ ] 历史记录管理：保存生成记录，支持回看和重用
- [ ] Windows 可执行程序打包（PyInstaller）
- [ ] 自动化测试覆盖核心流程
- [ ] 手动验证最终视频质量

## Out of Scope

- 实时流式生成（本版本为离线批量处理）
- 多语言支持（首版聚焦中文，后续扩展）
- 云端部署 / Web 服务
- 视频编辑功能（剪辑、特效、字幕）
- 模型训练 / 微调（仅使用预训练模型）

## 验收标准

- [ ] 输入一张人物照片 + 一段参考音频（≥5秒）+ 一段文本，能生成该人物"说话"的视频
- [ ] 生成视频的唇形与音频内容同步，肉眼可辨
- [ ] 生成语音的音色与参考音频相似
- [ ] GUI 界面可操作，非技术人员能使用
- [ ] Windows 下双击 exe 即可运行，无需额外安装
- [ ] 自动化测试覆盖 TTS 模块和唇形模块的输入输出

## 验证方式

- **方式**：两者结合
- **具体步骤**：
  1. 自动化测试：编写 pytest 用例，验证 TTS 模块输出 wav 格式、唇形模块输出 mp4 格式、端到端流程不报错
  2. 手动验证：使用真实人物素材跑完整流程，检查视频质量、唇形同步效果、音色相似度
- **预期结果**：自动化测试全部通过；手动验证视频自然、无明显瑕疵

## 依赖

- 无（独立开发，不依赖外部任务）

## 备选方案

- **技术路线 A（选定）**：集成 GPT-SoVITS（语音克隆）+ MuseTalk（唇形驱动），效果优先
- **技术路线 B**：自研轻量模型，体积优先但效果打折
- **混合方案**：核心用开源但做精简裁剪控制体积

## 参考

- GPT-SoVITS: https://github.com/RVC-Boss/GPT-SoVITS
- MuseTalk: https://github.com/TMElyralab/MuseTalk
- Wav2Lip (备选): https://github.com/Rudrabha/Wav2Lip
- SadTalker (备选): https://github.com/OpenTalker/SadTalker
- MyWorkflow: https://github.com/feelmeu/MyWorkflow

---

## 完成记录

<!-- issue done 时填写，一句话即可 -->
