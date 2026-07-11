# TIME FLIES — Xiaomi Smart Band 10 Pro research project

## v0.7.0：目标证据分层

项目继续保留两个候选画布，但从本版本开始，不再把“屏幕规格”和“可编译兼容性”混为一谈。

每个 target profile 分别记录：

- `hardware`：屏幕或画布证据。
- `buildChain`：编辑器或编译链证据。
- `deviceTarget`：Smart Band 10 Pro 是否接受生成包的证据。

只有 `deviceTarget: verified` 的配置，才能称为已验证的 10 Pro 构建目标。

## 当前候选配置

| Profile | Canvas | 主要价值 | 关键限制 |
| --- | --- | --- | --- |
| `compat-336x480` | 336×480 | Mi Band 8/9 Pro 的 MiCreate 构建链已有真机参考 | 没有 10 Pro 安装验证 |
| `experimental-400x480` | 400×480 | 10 Pro 已正式发布；发布前资料报告面板为 480×400 | 没有公开编译器目标或包元数据 |

默认仍使用 `compat-336x480`，因为它拥有更强的构建链证据；`experimental-400x480` 是当前更强的硬件布局候选。

## 当前功能

- 原 TIME FLIES 图片小时和分钟。
- 日期和星期图片。
- 天气图标及当天最低、最高温。
- 步数、最近心率和十级电量图片。
- 支持时显示中文节日或节气。
- 157 个经过验证的 RGBA PNG 素材。
- 项目校验器、`app.json` 生成器和目标配置切换器。
- MiCreate `.fprj` 格式探针与生成器。
- GitHub Actions 自动语法、结构和 target profile 检查。

## Profile schema

```text
targets/
├── README.md
├── profile.schema.json
├── compat-336x480.json
└── experimental-400x480.json
```

校验所有候选配置：

```bash
python tools/validate_target_profiles.py targets
```

切换目标配置：

```bash
python tools/apply_target_profile.py . targets/compat-336x480.json
python tools/apply_target_profile.py . targets/experimental-400x480.json
```

应用后运行：

```bash
python tools/validate_project.py .
```

应用脚本会拒绝以下配置：

- 非法或负数画布。
- `panelX` 超出屏幕。
- 右侧数据栏有效宽度小于 80px。
- 未知的 profile 状态。
- 缺失证据字段的旧格式配置。

## v0.7.0 实际校验

- 两个 profile 均通过 schema 和几何校验。
- `compat-336x480` 的右栏有效内容宽度为 128px。
- `experimental-400x480` 的右栏有效内容宽度为 172px。
- 两个 profile 均能在临时工程中应用，并正确更新 JS 常量、`app.js` 和 `app.json.example`。
- GitHub Actions 会逐个切换所有候选 profile 后运行项目校验。

## 当前最强证据

Smart Band 10 Pro 已于 2026 年 5 月公开发布，公开发布报道一致提到 1.74 英寸 AMOLED 屏幕；`480 × 400` 仍主要来自发布前报道。当前仍没有公开的 EasyFace/MiCreate 10 Pro 目标、`deviceSource`、原厂表盘包或已复现的真机安装结果。

详细证据见：

- `TARGET_RESEARCH.md`
- `COMPILER_RESEARCH.md`
- `MICREATE_FORMAT.md`
- `reference/mi-band-9-pro/`

## 当前状态

这是开发源码，不是可安装的 Smart Band 10 Pro 表盘。剩余关键阻塞项是：

- Smart Band 10 Pro 官方或已验证的编译目标。
- 真实 10 Pro 官方/第三方表盘包。
- 可确认的设备型号、包头或平台标识。
- MiCreate 或 EasyFace 在 Windows 上的实际打开、构建结果。
- 模拟器或真机安装测试。
