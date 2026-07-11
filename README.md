# 小米手环 NFC 自制表盘

这个仓库用于整理和维护小米手环 NFC 自制表盘资源。

## 下载表盘

成品 `.bin` 文件放在 GitHub Releases 中，主分支不保存可安装成品文件。

- Release：`v1.0.0`
- 下载页面：https://github.com/sep1107/miband-watchfaces/releases/tag/v1.0.0

| 文件 | 说明 |
| --- | --- |
| `miband7.bin` | 小米手环 7 NFC 原始表盘 |

## Xiaomi Smart Band 10 Pro 开发状态

当前研究版本为 **v0.8.0**。真实设备和 Mi Fitness 表盘缓存已经确认官方目标：

```text
设备型号：M2551B1
系统：Xiaomi HyperOS 3.101.030
表盘目标：P67
Watch OS：vela
画布：336×480
分辨率代号：XMHD03
包类型：BIN
能力协议：1.9.4
图片格式：indexed8
压缩：RLEReversed
```

项目已加入：

- 脱敏的 P67 真机包基准；
- `p67-336x480` 正式目标 profile；
- P67 profile 提取器；
- `resource.bin` 头部解析；
- target schema、profile 校验和遗留画布检查；
- GitHub Actions 自动重建并核对 P67 profile。

官方包目标已经验证，但自制 BIN 的真机安装仍未验证。当前重点是复现 `manifest.xml + indexed8/RLEReversed 资源 -> resource.bin` 的生成链。

## 仓库结构

```text
source/miband10pro/
├── reference/real-device/
│   ├── M2551B1.json
│   └── P67-baseline/
├── project/
│   ├── REAL_DEVICE_PACKAGE.md
│   └── targets/p67-336x480.json
└── tools/
    ├── extract_p67_profile.py
    ├── validate_target_profiles.py
    └── check_no_legacy_canvas.py
```

## 文件信息

- `miband7.bin`：约 209 KB
- SHA-256：`8caf6df2d77a6829545ddfbe3ec6ff8f9e380e2bfebdaeb76dcb1a75352df1e4`
