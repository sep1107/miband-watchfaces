# Mi Band 10 Plus 开发目录

本目录分成两部分：

```text
source/miband10plus/
├── README.md
├── reference/
│   └── amazfit-band7/
└── project/
```

## reference

保存拆出的原始参考工程，尽量保持原包目录和代码不变，用于研究 Zepp OS 的配置、控件和布局方式。

## project

用于真正编写 Mi Band 10 Plus 适配版。这里的文件可以修改，不会污染参考工程。

## 当前进度

- 已确认上传包是 Zepp OS 表盘包。
- 已拆出 `device.zip` 与 `app-side.zip`。
- 已找到可读布局源码 `watchface/default-target/index.js`。
- 原参考设备为 Amazfit Band 7，配置中的 `designWidth` 为 `194`。
- 参考布局目前只实现一个节日/节气文本控件，坐标为 `x:57, y:308, w:77, h:22`。

## 下一步

1. 确认 Mi Band 10 Plus 的正式设备名称、屏幕分辨率和 Zepp OS 目标配置。
2. 在 `project/` 建立目标设备工程。
3. 将 TIME FLIES 的资源和功能迁移到新工程。
4. 编译并进行模拟器或真机测试。
