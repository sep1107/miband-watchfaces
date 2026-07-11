# Xiaomi Smart Band 10 Pro 表盘开发目录

本目录用于开发 TIME FLIES 的 Xiaomi Smart Band 10 Pro 版本。

## v0.7.2 真机证据

用户提供的实机照片已经确认：

```text
设备：小米手环10 Pro
型号：M2551B1
系统：Xiaomi HyperOS
OS 版本：3.101.030
```

照片不提交到仓库；非敏感事实记录在：

```text
reference/real-device/M2551B1.json
```

这验证了真实设备身份和固件家族，但不等于已经得到可安装表盘目标。

## 目标策略

项目保留两个候选配置，并分别衡量硬件、构建链和真机目标证据：

```text
构建链参考：compat-336x480
硬件布局候选：experimental-400x480
```

- `compat-336x480` 基于公开的 Mi Band 9 Pro 真机验证 MiCreate 工程，构建链证据更强；实机照片中的屏幕比例也更接近这个候选，但照片不能证明精确像素。
- `experimental-400x480` 对应发布前报道的宽屏参数，但没有公开编译目标。
- 两者都尚未通过 Smart Band 10 Pro 真机安装验证。

## 目录

```text
miband10pro/
├── README.md
├── MICREATE_FORMAT.md
├── micreate-probe/
├── reference/
│   ├── amazfit-band7/
│   ├── mi-band-9-pro/
│   ├── original-band7/
│   └── real-device/
│       └── M2551B1.json
├── project/
│   ├── README.md
│   ├── COMPILER_RESEARCH.md
│   ├── TARGET_RESEARCH.md
│   ├── PACKAGE_INSPECTION.md
│   ├── required-assets.json
│   ├── targets/
│   └── device/
└── tools/
    ├── prepare_assets.py
    ├── validate_project.py
    ├── validate_target_profiles.py
    ├── inspect_watchface_package.py
    ├── build_app_json.py
    ├── build_micreate_probe.py
    └── apply_target_profile.py
```

## 当前状态

- 已确认真实设备型号 `M2551B1` 和 HyperOS `3.101.030`。
- 已接入图片时间、日期、星期、天气、步数、心率、电量与节日。
- 已整理并验证 157 个 RGBA PNG 资源。
- 已加入 target profile schema、证据分层和几何校验。
- GitHub Actions 会逐个应用所有候选 profile 并运行项目校验。
- 已提供 MiCreate `.fprj` 格式探针。
- 已加入递归表盘包检查器，可识别嵌套 ZIP、JSON/XML、PNG/TGA 和设备元数据。
- 尚未获得 10 Pro 原厂/第三方表盘包、`deviceSource`、正式编译配置或自制表盘真机安装结果。
- 当前项目还不是可安装成品。
