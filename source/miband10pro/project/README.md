# TIME FLIES — Xiaomi Smart Band 10 Pro research project

## v0.7.2：真机身份已确认

用户提供的实机照片已经确认：

```text
设备：小米手环10 Pro / Xiaomi Smart Band 10 Pro
型号：M2551B1
系统：Xiaomi HyperOS
OS 版本：3.101.030
```

照片本身不提交到仓库，只保存推导出的非敏感设备信息。结构化记录位于：

```text
reference/real-device/M2551B1.json
```

这解决了“目标设备到底是什么”的问题，但尚未解决表盘包格式、`deviceSource`、MiCreate `DeviceType` 和真机安装兼容性。

## 目标证据分层

项目不会把“屏幕规格”“可用编译链”和“真机兼容性”混为一谈。

每个 target profile 分别记录：

- `hardware`：屏幕或画布证据。
- `buildChain`：编辑器或编译链证据。
- `deviceTarget`：Smart Band 10 Pro 是否接受生成包的证据。

只有 `deviceTarget: verified` 的配置，才能称为已验证的 10 Pro 构建目标。

## 当前候选配置

| Profile | Canvas | 主要价值 | 关键限制 |
| --- | --- | --- | --- |
| `compat-336x480` | 336×480 | Mi Band 8/9 Pro 的 MiCreate 构建链已有真机参考；实机照片的屏幕比例也更接近该候选 | 还没有 10 Pro 安装验证 |
| `experimental-400x480` | 400×480 | 对应发布前报道的 480×400 面板数据 | 没有公开编译器目标或包元数据 |

默认仍使用 `compat-336x480`，因为它拥有更强的构建链证据；照片只提供视觉支持，不能单独证明真实像素分辨率。

## 当前功能

- 原 TIME FLIES 图片小时和分钟。
- 日期和星期图片。
- 天气图标及当天最低、最高温。
- 步数、最近心率和十级电量图片。
- 支持时显示中文节日或节气。
- 157 个经过验证的 RGBA PNG 素材。
- 项目校验器、`app.json` 生成器和目标配置切换器。
- MiCreate `.fprj` 格式探针与生成器。
- GitHub Actions 自动语法、结构、profile 和包检查。
- 递归表盘包检查器。

## 表盘包检查器

```bash
python tools/inspect_watchface_package.py package.face \
  --json package-report.json \
  --markdown package-report.md
```

它支持 ZIP 型 `.bin`、`.zpk`、嵌套 ZIP、MiCreate `.fprj/.info/.face`、JSON/XML、PNG/TGA，并会寻找：

- `deviceSource`
- `DeviceType`
- `DeviceVersion`
- `designWidth`
- 型号名、HyperOS、Zepp、MiCreate、EasyFace、`gts`、`nxp`

## 当前最关键的下一步

从这台型号为 `M2551B1`、系统为 HyperOS `3.101.030` 的真机配套 Mi Fitness 中取得一个表盘包或缓存文件。拿到后，现有检查器可以直接判断：

- 是否为 `.face`、`.bin`、`.zpk` 或其他格式；
- 实际画布尺寸；
- 设备型号和平台标识；
- 是否沿用 Mi Band 8/9 Pro 的 `DeviceType=11`；
- 是否需要 EasyFace、MiCreate 或另一套工具链。

## 当前状态

这是开发源码，不是可安装的 Smart Band 10 Pro 表盘。已经确认真实设备型号与系统版本，但仍缺：

- 原厂或第三方 10 Pro 表盘包；
- 可确认的 `deviceSource` / `DeviceType`；
- MiCreate 或 EasyFace 在 Windows 上的实际构建结果；
- 真机安装测试。
