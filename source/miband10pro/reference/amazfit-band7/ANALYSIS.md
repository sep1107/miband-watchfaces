# 拆包分析

## 外层文件

```text
1019041-七的表盘-1.0.1-1677381331.zip
├── default-target-DIALOG-194x368.zpk
├── .sc
└── manifest.json
```

`default-target-DIALOG-194x368.zpk` 本身是 ZIP，里面包含：

```text
device.zip
app-side.zip
```

## device.zip

```text
app.js
app.json
assets/1.png
assets/2.png
watchface/default-target/index.js
```

## 关键配置

- 原目标设备：Amazfit Band 7
- `deviceSource`：252、253、254
- `designWidth`：194
- 运行时 API：1.0.0 ～ 1.0.1
- 原包版本：1.0.1

## index.js 实际内容

该源码只有一个可见文本控件：

```text
类型：hmUI.widget.TEXT
x: 57
y: 308
w: 77
h: 22
text_size: 17
```

它通过 `hmSensor.id.TIME` 调用 `getShowFestival()`，显示节日或节气文字。

该源码没有包含：

- 数字时间布局
- 日期布局
- 天气布局
- 电量布局
- 步数或心率布局
- 图片式数字资源映射

因此它适合作为 Zepp OS 表盘工程结构和 API 用法参考，但不是完整的 TIME FLIES 表盘模板。

## 资源文件

`assets/1.png` 与 `assets/2.png` 虽然后缀是 `.png`，文件内容实际为 TGA 预览资源。

## 对 Smart Band 10 Pro 开发的意义

可借鉴：

- Zepp OS `app.json` 结构
- `app.js` 启动方式
- `DeviceRuntimeCore.WatchFace` 生命周期
- `hmUI.createWidget` 控件创建方式
- `hmSensor.id.TIME` 数据读取方式

不能直接复用：

- Amazfit Band 7 平台 ID
- 原 194 宽度坐标
- 原资源尺寸
- 完整 TIME FLIES 布局
