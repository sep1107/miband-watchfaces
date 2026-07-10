# Mi Band 10 Plus 适配工程

> 当前暂按 Xiaomi Smart Band 10 的 `212 × 520` 屏幕建立开发骨架。
>
> 公开型号中暂未确认正式名称为 “Mi Band 10 Plus” 的独立设备，因此设备平台 ID 和最终包格式仍需在编译前确认。

## 目录

```text
project/
├── README.md
└── device/
    ├── app.json.example
    ├── app.js
    ├── assets/
    │   └── .gitkeep
    └── watchface/
        └── default-target/
            └── index.js
```

## 当前阶段

- 已建立 212 × 520 的布局坐标系。
- 已加入 TIME FLIES 标题、时间文本和节日文本的初始控件。
- `app.json.example` 暂不包含未验证的设备 `deviceSource`。
- 当前代码属于开发骨架，尚未经过 Mi Band 10 真机或模拟器编译验证。

## 后续

1. 确认 Mi Band 10 对应的设备平台 ID、包格式和编译器版本。
2. 将原 TIME FLIES 图片资源迁入 `assets/`。
3. 按 212 × 520 重新计算时间、日期、天气和状态图标位置。
4. 使用 EasyFace Gen2 或匹配的编译链进行首次构建。
