# Source

这个目录用于存放表盘原始资源。

整理规则：

- 原始压缩包里的 `7677/` 外层目录不保留。
- `7677.bin` 不上传；成品表盘按设备放在 `watchfaces/` 目录下。
- `__MACOSX/` 不上传。
- 推荐目录结构：

```text
source/
├── app.json
├── app.bin
├── watchface/
│   └── index.bin
└── assets/
    └── images/
```

当前上传的原始包已按这个规则清理。
