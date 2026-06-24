---
role: needs-triage
title: Windows 可执行程序打包
created_at: 2026-06-24
importance: mid
---

# 0007 — Windows 可执行程序打包

## 目标

将整个应用打包为 Windows 双击即用的 exe 程序。

## In Scope

- [ ] PyInstaller 配置
- [ ] 模型文件管理策略（首次运行下载 / 用户指定路径）
- [ ] CUDA/PyTorch 依赖打包
- [ ] FFmpeg 打包
- [ ] 安装程序制作（可选）
- [ ] 启动脚本

## Out of Scope

- 自动更新机制
- 多平台打包（仅 Windows）

## 验收标准

- [ ] Windows 10+ 下双击 exe 可运行
- [ ] 无需额外安装 Python/CUDA
- [ ] 首次运行引导用户配置模型路径

## 验证方式

- **方式**：手动验证
- **具体步骤**：在干净 Windows 环境测试
- **预期结果**：程序正常启动和运行

## 依赖

- Issue #0006（需要 GUI 完成）

---

## 完成记录
