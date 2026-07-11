# TIME FLIES — Xiaomi Smart Band 10 Pro P67 project

## v0.8.1 目标

项目唯一正式目标是：

```text
M2551B1 / P67 / vela / 336x480 / XMHD03 / BIN
```

这一结论来自真实设备和 Mi Fitness 表盘缓存，而不是媒体规格或相关型号推断。

## 已验证的官方包结构

```text
capability.json
├── protocol = 1.9.4
├── resolution = XMHD03
├── region = CN
└── packet = BIN

description.xml
├── deviceType = P67
├── size = 336x480
├── watchOS = vela
├── imageFormat = indexed8
└── imageCompression = true

manifest.xml
├── width = 336
├── height = 480
├── compressMethod = RLEReversed
└── editable = true

resource.bin
├── magic = 0x1234A55A
├── header = 168 bytes
├── P67 theme entry = 176 bytes
├── RecordBase = 16 bytes
├── embedded package ID = 120917384229
└── theme count = 3
```

## v0.8.1 二进制进展

真实 `resource.bin` 已在本地通过 `inspect_p67_binary.py` 完成结构校验：

```text
Theme core: 88 bytes
Theme extension: 88 bytes
Record area: offset 696
Raw-data area: offset 4344
Total records: 228
Structural errors: 0
```

记录类型统计：

- Layout：60
- Image：45
- ImageArray：27
- Translation：9
- Data：48
- Slot：3
- Widget：36

这说明 Header、扩展 Theme 表、RecordBase 表和 payload 地址边界已经可以自动解析。原始官方二进制及图片不会提交到仓库，只保存脱敏后的结构结论。

## 当前代码定位

`device/` 下的 JavaScript 工程是布局和数据展示原型，不是 P67 编译器输入。P67 工作集中在：

- `targets/p67-336x480.json`
- `REAL_DEVICE_PACKAGE.md`
- `../reference/real-device/P67-baseline/`
- `../tools/extract_p67_profile.py`
- `../tools/inspect_p67_binary.py`
- `../tools/validate_target_profiles.py`

## 下一里程碑

1. 精确解析 Image、ImageArray、Data、Slot 和 Widget payload；
2. 将 TIME FLIES 素材转换为 `indexed8`；
3. 实现并验证 `RLEReversed` 编码；
4. 生成最小单主题 P67 BIN；
5. 静态校验通过后，再在 M2551B1 真机上测试安装。
