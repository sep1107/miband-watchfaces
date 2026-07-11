# TIME FLIES — Xiaomi Smart Band 10 Pro research project

## v0.6.1 目标配置

项目提供两个候选目标配置：

- **主要候选：`compat-336x480`** — 基于已在 Mi Band 9 Pro 真机测试的 MiCreate 工程。
- **实验候选：`experimental-400x480`** — 保留用于对比部分媒体报道中的 `480 × 400` 面板说法。

在获得真实 Smart Band 10 Pro 表盘包、编译目标或设备元数据前，两者都不声称是最终兼容配置。

## 当前功能

- 原 TIME FLIES 图片小时和分钟。
- 日期和星期图片。
- 天气图标及当天最低、最高温。
- 步数、最近心率和十级电量图片。
- 支持时显示中文节日或节气。
- 157 个经过验证的 RGBA PNG 素材。
- 项目校验器、`app.json` 生成器和目标配置切换器。
- MiCreate `.fprj` 格式探针与生成器。
- GitHub Actions 自动语法和结构检查。

## 切换目标配置

```bash
python tools/apply_target_profile.py . targets/compat-336x480.json
python tools/apply_target_profile.py . targets/experimental-400x480.json
```

切换后运行：

```bash
python tools/validate_project.py .
```

## MiCreate Pro 格式探针

仓库新增：

```text
source/miband10pro/
├── micreate-probe/
│   └── TimeFlies_ProProbe.fprj
├── MICREATE_FORMAT.md
└── tools/build_micreate_probe.py
```

探针使用从真机测试的 Mi Band 8/9 Pro 工程中观察到的 `DeviceType="11"`，包含 16 个控件：背景、图片时间、日期、星期、天气、步数、心率和电量。

该值只是 Pro 格式参考，**尚未验证适用于 Smart Band 10 Pro**。生成器要求显式传入：

```bash
python tools/build_micreate_probe.py \
  project/device/assets \
  micreate-probe \
  --accept-reference-device-type
```

生成器会自动创建天气负号 PNG，不再依赖额外素材；电量图片使用 0%、10%……90% 阈值。

完整探针图片包：`time-flies-micreate-probe-v0.2.zip`

- 69 张 PNG
- 336 × 480 预览图
- SHA-256：`7a5735e3bcf22ee5cc73832b0f22868712465a68b881a24a7364554da7f101a5`

## 为什么主要候选改为 336 × 480

找到的公开 Mi Band 9 Pro 真机项目使用 MiCreate `.fprj` 工程、`336 × 480` 示例图和 Mi Band 8 Pro 目标元数据生成 `.face` 文件。由于 9 Pro 与 10 Pro 都属于宽屏 Pro 产品路线，这是一条比媒体规格更接近真实表盘开发链的参考，但仍不能代替 10 Pro 真机验证。

更多证据见：

- `TARGET_RESEARCH.md`
- `reference/mi-band-9-pro/`
- `COMPILER_RESEARCH.md`
- `MICREATE_FORMAT.md`

## v0.6.1 校验

- 默认 `compat-336x480` 配置通过 JavaScript 和项目校验。
- `experimental-400x480` 配置通过切换和项目校验。
- 运行时必需的 57 个素材通过验证。
- 完整开发包中的 157 个 PNG 全部通过格式验证。
- MiCreate 探针 XML 可重新解析，16 个控件的 69 张图片引用均存在。
- GitHub 工作流会检查 JavaScript、Python 工具、配置生成和探针 XML。

## 当前状态

这是开发源码，不是可安装的 Smart Band 10 Pro 表盘。剩余关键阻塞项是：

- Smart Band 10 Pro 官方或已验证的编译目标。
- 真实 10 Pro 官方/第三方表盘包。
- 可确认的设备型号、包头或平台标识。
- MiCreate 或 EasyFace 在 Windows 上的实际打开、构建结果。
- 模拟器或真机安装测试。
