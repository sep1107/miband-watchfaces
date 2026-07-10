# 小米手环 NFC 自制表盘

这个仓库用于整理和维护小米手环 NFC 自制表盘资源。

## 下载表盘

成品 `.bin` 文件放在 GitHub Releases 中，主分支不保存可安装成品文件。

- Release：`v1.0.0`
- 下载页面：https://github.com/sep1107/miband-watchfaces/releases/tag/v1.0.0

| 文件 | 说明 |
| --- | --- |
| `miband7.bin` | 小米手环 7 NFC 原始表盘 |
| `miband9.bin` | 实验性副本，尚未经过小米手环 9 真机或专用编译器验证 |

> 注意：当前 `miband9.bin` 与 `miband7.bin` 的内容完全相同。两者使用相同的 SHA-256，不能仅凭同为 192 × 490 分辨率就认定兼容。详细检查见 `docs/MIBAND9_COMPATIBILITY.md`。

## 仓库结构

```text
miband-watchfaces/
├── README.md
├── docs/
│   └── MIBAND9_COMPATIBILITY.md
└── source/
    ├── README.md
    ├── app.json
    ├── app.bin
    └── miband10plus/
        ├── README.md
        ├── reference/
        │   └── amazfit-band7/
        └── project/
```

- `source/app.json`、`source/app.bin`：原 TIME FLIES 表盘保留下来的核心配置和编译组件。
- `source/miband10plus/reference/`：保存拆出的参考工程，保持原始结构。
- `source/miband10plus/project/`：Mi Band 10 适配开发工程。

## Mi Band 10 适配状态

已经找到并拆出一个 Amazfit Band 7 Zepp OS 表盘工程。它包含可读的 `watchface/default-target/index.js`，可用于分析 Zepp OS 控件、坐标和布局逻辑。

目标画布暂按 Xiaomi Smart Band 10 的 `212 × 520` 处理。参考工程不是 Mi Band 10 成品；开发代码放在 `project/`，不会直接修改参考源码。

## 使用说明

1. 打开 Releases 页面。
2. 下载对应设备的 `.bin` 文件。
3. 使用支持该设备和包格式的工具进行安装。
4. 安装前建议先备份原表盘文件。
5. `miband9.bin` 目前仅供实验，不建议在无法恢复设备的情况下尝试。

## 文件信息

- `miband7.bin`：约 209 KB
- `miband9.bin`：约 209 KB，内容与 Mi Band 7 文件相同，状态为未验证
- SHA-256：`8caf6df2d77a6829545ddfbe3ec6ff8f9e380e2bfebdaeb76dcb1a75352df1e4`
