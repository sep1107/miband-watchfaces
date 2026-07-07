# 小米手环 NFC 自制表盘

这个仓库用于存放小米手环 NFC 的自制表盘文件。

## 表盘文件

| 文件 | 说明 |
| --- | --- |
| `watchfaces/miband7.bin` | 小米手环 7 NFC 自制表盘文件 |
| `watchfaces/miband9.bin` | 小米手环 9 NFC 兼容版表盘文件；与手环 7 同分辨率版本 |

## 原始资源说明

原始资源建议放在 `source/` 目录下，且不保留外层 `7677/` 文件夹。

清理规则：

- 不上传 `7677.bin`，因为仓库已经按设备分别提供 `miband7.bin` 和 `miband9.bin`。
- 不上传 `__MACOSX/` 目录。
- `app.json`、`app.bin`、`watchface/`、`assets/` 应直接位于 `source/` 下。

## 使用说明

1. 下载对应设备的 `.bin` 文件。
2. 使用支持小米手环 NFC 表盘导入/替换的工具进行安装。
3. 安装前建议先备份原表盘文件。

## 文件信息

- `miband7.bin`：约 209 KB
- `miband9.bin`：约 209 KB，同分辨率兼容版
- SHA-256：`8caf6df2d77a6829545ddfbe3ec6ff8f9e380e2bfebdaeb76dcb1a75352df1e4`
