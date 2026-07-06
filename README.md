# 🖼 图片尺寸转换工具

> 一键将任意尺寸图片裁切/缩放至 **Apple / Google Play / 华为 / 三星 / 社交平台** 等 50+ 预设尺寸。

纯 macOS 内置 `sips` 实现，**零外部依赖**，无需 `pip install`。

---

## 🚀 快速开始

```bash
# 系统自带 Python 3.9+ 即可
python3 image_resizer.py

# 或指定 Python 3.11（推荐，有更完整的类型支持）
python3.11 image_resizer.py
```

---

## 📋 预设尺寸（50+）

| 分类 | 覆盖范围 |
|------|----------|
| 🍎 **Apple** | iPhone 14 Pro Max / 14 Plus / 14 Pro / 13 Pro Max / SE、iPad Pro 12.9" / 11" / mini、Apple Watch 49/45/41mm、Mac 16:10 / 14" |
| 🤖 **Google Play** | 手机截图（竖/横）、平板 7" / 10"、Feature Graphic、TV Banner、Wear OS、应用图标 |
| 🛒 **第三方商店** | 华为 AppGallery、三星 Galaxy Store、小米 GetApps、OPPO 软件商店、vivo 应用商店、腾讯应用宝、TapTap |
| 🌐 **通用 / 社交** | 16:9 / 4:3 / 1:1、微信公众号封面、视频号封面、小红书、Instagram、Twitter/X、LinkedIn |
| ✏️ **自定义** | 每个分类下均可手动输入任意宽高 |

---

## 🎯 裁切模式

| 模式 | 说明 |
|------|------|
| **fit** 等比缩放 | 保持原始比例，缩放至目标范围内 |
| **fill** 拉伸填充 | 忽略比例，强制拉伸至目标尺寸 |
| **crop** 居中裁切 | 先等比放大填满 → 再居中裁掉多余部分（**最常用**） |

---

## 🔧 使用说明

1. **添加图片** — 点击「➕ 添加图片」批量选择（支持 png / jpg / heic / webp / avif 等）
2. **选择分类** — 从分类下拉切换平台
3. **选择预设** — 从预设下拉选目标尺寸（宽高自动填充）
4. **选裁切模式** — 一般用「居中裁切 crop」
5. **选输出路径** — 默认桌面，可改为其他目录
6. **开始转换** — 日志面板实时显示每张图处理状态

---

## 📝 示例

```
分类: 🍎 Apple  →  预设: iPhone 通用投放  →  1242 × 2688
分类: 🤖 Google Play  →  预设: 手机截图 (竖屏)  →  1080 × 1920
分类: 🌐 通用/社交  →  预设: 微信公众号封面  →  900 × 383
```

输出文件名格式：`原文件名_宽x高.扩展名`

---

## ⚙️ 技术细节

- **图片引擎**：macOS 内置 [`sips`](https://ss64.com/osx/sips.html)（Scriptable Image Processing System）
- **GUI 框架**：Python 内置 `tkinter`
- **线程模型**：`queue.Queue` 消息总线，工作线程不碰 UI
- **超时保护**：单张图 60s 超时，不会无限卡死
- **取消支持**：转换中可随时取消

---

## 📦 项目结构

```
.
├── image_resizer.py    # 主程序（单文件）
├── README.md           # 本文件
└── .gitignore
```

---

## 📄 License

MIT
