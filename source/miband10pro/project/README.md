# TIME FLIES — Xiaomi Smart Band 10 Pro research project

## v0.6.0 目标配置纠正

项目现在提供两个候选目标配置：

- **主要候选：`compat-336x480`** — 基于已在 Mi Band 9 Pro 真机测试的 MiCreate 工程。
- **实验候选：`experimental-400x480`** — 仅保留用于对比部分媒体报道中的 `480 × 400` 面板说法。

在获得真实 Smart Band 10 Pro 表盘包、编译目标或设备元数据前，两者都不声称是最终兼容配置。

## 当前功能

- 原 TIME FLIES 图片小时和分钟。
- 日期和星期图片。
- 天气图标及当天最低、最高温。
- 步数、最近心率和十级电量图片。
- 支持时显示中文节日或节气。
- 157 个经过验证的 RGBA PNG 素材。
- 项目校验器、`app.json` 生成器和目标配置切换器。

## 切换目标配置

```bash
python tools/apply_target_profile.py . targets/compat-336x480.json
python tools/apply_target_profile.py . targets/experimental-400x480.json
```

切换后运行：

```bash
python tools/validate_project.py .
```

## 为什么改为 336 × 480

找到的公开 Mi Band 9 Pro 真机项目使用 MiCreate `.fprj` 工程、`336 × 480` 示例图和 Mi Band 8 Pro 目标元数据生成 `.face` 文件。由于 9 Pro 与 10 Pro 都属于宽屏 Pro 产品路线，这是一条比媒体规格更接近真实表盘开发链的参考，但仍不能代替 10 Pro 真机验证。

更多证据见：

- `TARGET_RESEARCH.md`
- `reference/mi-band-9-pro/`
- `COMPILER_RESEARCH.md`

## v0.6.0 校验

- 默认 `compat-336x480` 配置通过 JavaScript 和项目校验。
- `experimental-400x480` 配置通过切换和项目校验。
- 运行时必需的 57 个素材通过验证。
- 完整包中的 157 个 PNG 全部通过格式验证。
- 完整开发包 SHA-256：`544307e63a5e70333a3c92b8a5de6e5bfd02a35efc3f85e27d0bc7d9142b006e`。

## 当前状态

这是开发源码，不是可安装的 Smart Band 10 Pro 表盘。剩余关键阻塞项是：

- Smart Band 10 Pro 官方或已验证的编译目标。
- 真实 10 Pro 官方/第三方表盘包。
- 可确认的设备型号、包头或平台标识。
- 模拟器或真机安装测试。
