# 小米手环 NFC 自制表盘

这个仓库用于整理和维护小米手环 NFC 自制表盘资源。

## 下载表盘

成品 `.bin` 文件放在 GitHub Releases 中，主分支不保存可安装成品文件。

- Release：`v1.0.0`
- 下载页面：https://github.com/sep1107/miband-watchfaces/releases/tag/v1.0.0

| 文件 | 说明 |
| --- | --- |
| `miband7.bin` | 小米手环 7 NFC 原始表盘 |

## 仓库结构

```text
miband-watchfaces/
├── README.md
├── .github/workflows/
│   ├── validate-watchface.yml
│   └── validate-band10pro.yml
└── source/
    ├── README.md
    ├── app.json
    ├── app.bin
    └── miband10pro/
        ├── README.md
        ├── MICREATE_FORMAT.md
        ├── micreate-probe/
        │   └── TimeFlies_ProProbe.fprj
        ├── reference/
        │   ├── amazfit-band7/
        │   └── mi-band-9-pro/
        ├── project/
        │   └── targets/
        └── tools/
            ├── validate_project.py
            ├── apply_target_profile.py
            ├── build_app_json.py
            └── build_micreate_probe.py
```

## Xiaomi Smart Band 10 Pro 开发状态

当前研究版本为 `v0.6.1`，采用双目标配置：

- `compat-336x480`：主要兼容候选，依据是真机验证过的 Mi Band 9 Pro MiCreate 工程。
- `experimental-400x480`：保留用于对比尚未验证的宽屏参数。

目前源码已实现图片时间、日期、星期、天气、步数、心率、电量和节日信息，并加入：

- 目标配置切换
- 项目与资源校验
- `app.json` 生成器
- GitHub Actions 自动检查
- MiCreate `.fprj` 格式探针

MiCreate 探针使用 `DeviceType="11"` 作为 Mi Band 8/9 Pro 格式参考，包含 16 个控件和独立的 69 张图片包；这个值尚未验证适用于 Smart Band 10 Pro。

> 仍未获得 Smart Band 10 Pro 的正式 SDK、已验证目标配置、官方表盘包或真机测试，因此当前项目是研究与开发源码，不是可安装成品。

## 文件信息

- `miband7.bin`：约 209 KB
- SHA-256：`8caf6df2d77a6829545ddfbe3ec6ff8f9e380e2bfebdaeb76dcb1a75352df1e4`
