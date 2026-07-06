---
version: alpha
name: FrameKit
description: 干净克制的 macOS 工具风格 — 蓝调主导，留白呼吸，信息层级清晰。
colors:
  primary: "#2563EB"
  primary-hover: "#1D4ED8"
  text: "#0F172A"
  text-secondary: "#64748B"
  text-muted: "#94A3B8"
  bg-page: "#F8FAFC"
  bg-card: "#FFFFFF"
  bg-input: "#F1F5F9"
  border: "#E2E8F0"
  border-focus: "#93C5FD"
  success: "#16A34A"
  error: "#DC2626"
  warn: "#D97706"
  white: "#FFFFFF"
typography:
  h1:
    fontFamily: "system-ui, -apple-system, 'SF Pro Display', sans-serif"
    fontSize: 20px
    fontWeight: 700
  body:
    fontFamily: "system-ui, -apple-system, 'SF Pro Text', sans-serif"
    fontSize: 13px
    fontWeight: 400
  body-sm:
    fontFamily: "system-ui, -apple-system, 'SF Pro Text', sans-serif"
    fontSize: 11px
    fontWeight: 400
  code:
    fontFamily: "'SF Mono', 'Monaco', 'Menlo', monospace"
    fontSize: 12px
    fontWeight: 400
  label:
    fontFamily: "system-ui, -apple-system, 'SF Pro Text', sans-serif"
    fontSize: 12px
    fontWeight: 600
    letterSpacing: "0.02em"
    textTransform: uppercase
rounded:
  sm: 4px
  md: 8px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: 10px
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: "{colors.bg-input}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: 8px
  button-secondary-hover:
    backgroundColor: "{colors.border}"
  button-danger:
    backgroundColor: "{colors.error}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: 10px
  input:
    backgroundColor: "{colors.bg-input}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: 8px
  card:
    backgroundColor: "{colors.bg-card}"
    rounded: "{rounded.md}"
    padding: 16px
  badge:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.white}"
    rounded: "{rounded.full}"
    padding: 4px
---

## Overview

FrameKit — 为 macOS 桌面工具设计。克制、清晰，不做多余的装饰。
蓝色作为唯一的强调色，大面积留白，让操作路径一目了然。

## Colors

- **Primary (#2563EB):** 唯一强调色，按钮、进度条、选中态、链接。
- **Text (#0F172A):** 主文字，深 slate，确保可读性。
- **Text Secondary (#64748B):** 辅助信息、标签、提示。
- **Text Muted (#94A3B8):** 占位符、禁用态、时间戳。
- **BG Page (#F8FAFC):** 窗口底色，微弱暖灰避免纯白刺眼。
- **BG Card (#FFFFFF):** 卡片/列表区背景，与页面背景形成微妙分层。
- **BG Input (#F1F5F9):** 输入框背景，比页面稍深引导视线。
- **Border (#E2E8F0):** 分割线、边框。
- **Success (#16A34A):** 成功状态、日志 OK。
- **Error (#DC2626):** 错误状态、日志 ERROR。
- **Warn (#D97706):** 警告、取消。

## Typography

- 正文：system-ui 13px — macOS 默认阅读字号。
- 代码/Monaco：日志、文件路径用等宽字体。
- 标签：12px 600 weight + 0.02em letter-spacing，小写但清晰。
- 层次不超过 3 级：标题 > 正文 > 辅助。

## Layout

- 8px 基础网格，所有间距为 8 的倍数（4/8/12/16/24）。
- 窗口最小宽高保护，不自适应过小尺寸。
- 分组之间有明确的分割线或留白。

## Shapes

- macOS 风格的轻微圆角（4px 按钮，8px 卡片）。
- 输入框、按钮统一样式，不混用直角和圆角。

## Components

- **button-primary:** 蓝底白字，页面上唯一高强调操作（「开始转换」）。
- **button-secondary:** 浅灰底，批量操作（「添加」「移除」「清空」）。
- **button-danger:** 红色，中断操作（「取消」）。
- **input:** 浅灰背景无边框，聚焦时出现蓝色底部指示。
- **card:** 白底 8px 圆角，列表区域包裹。
- **badge:** 蓝色胶囊，文件计数、状态标记。

## Do's and Don'ts

- ✅ 用留白区分组，不用多余的框线
- ✅ 主操作只有一个高亮按钮
- ✅ 状态颜色始终搭配文字说明（不只是颜色）
- ❌ 不要同时出现多个鲜艳颜色争抢注意力
- ❌ 不要用纯黑 #000 或纯白 #FFF
- ❌ 不要用超过 3 级字号
