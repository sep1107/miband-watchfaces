# Source

这个目录保存表盘开发相关的配置、编译组件和适配工程。

```text
source/
├── README.md
├── app.json
├── app.bin
└── miband10pro/
    ├── README.md
    ├── reference/
    │   ├── amazfit-band7/
    │   └── mi-band-9-pro/
    ├── project/
    │   └── targets/
    └── tools/
```

- `app.json`、`app.bin`：原 TIME FLIES 表盘保留的核心配置和编译组件，并不是完整可重新编译工程。
- `miband10pro/reference/amazfit-band7/`：Zepp OS API 和工程结构参考。
- `miband10pro/reference/mi-band-9-pro/`：更接近 Pro 宽屏产品的 MiCreate 工程与元数据研究。
- `miband10pro/project/`：Xiaomi Smart Band 10 Pro 双目标开发工程。
- `miband10pro/tools/`：素材转换、项目校验、配置生成和目标切换工具。

当前主要候选画布为 `336 × 480`，并保留 `400 × 480` 实验配置。最终目标仍须由 Smart Band 10 Pro 的正式 SDK、已知可用表盘包或真机确认。
