# TIME FLIES — Xiaomi Smart Band 10 Pro

## 暂定开发目标

```text
开发版本：0.5.0
开发画布：400 × 480
目标型号：Xiaomi Smart Band 10 Pro
状态：尚未取得正式 SDK、deviceSource 或真机验证
```

画布方向和尺寸是当前开发参数，不代表最终设备规格。传感器逻辑与布局常量已经分开，后续确认正式配置后可以调整坐标而不必重写数据读取逻辑。

## 当前布局

```text
┌───────────────────┬──────────────────┐
│ 原 TIME FLIES     │ TIME FLIES       │
│ 仪表盘背景        │ 日期 / 星期      │
│                   │ 天气 / 高低温    │
│ 图片小时数字      │ 步数             │
│ 图片分钟数字      │ 心率             │
│                   │ 电量图 + 百分比  │
│                   │ 节日 / 节气      │
└───────────────────┴──────────────────┘
```

## 已实现的源码功能

- 小时与分钟使用原 TIME FLIES 图片数字动态显示。
- 当前日期。
- 星期图片动态切换。
- 当天天气图标以及最高、最低温。
- 步数。
- 最近一次心率。
- 电量百分比及十级电量图片。
- 支持时显示中文节日或节气。
- 传感器事件监听与销毁清理。
- 集中定义屏幕尺寸、面板位置和素材根目录。

## v0.5.0 新增

- 新增 `required-assets.json`，列出运行时实际引用的 57 个必需素材。
- 新增 `tools/validate_project.py`，用于校验配置、JavaScript 语法和 PNG 资源。
- 新增 `tools/build_app_json.py`，在拿到已验证的 `deviceSource` 后生成正式 `app.json`。
- 新增 GitHub Actions 工作流，对每次提交做文本源码校验。
- 新增 `COMPILER_RESEARCH.md`，记录 EasyFace v4.22 对普通 Mi Band 10 的支持以及 10 Pro 仍未确认的问题。

## 校验

完整开发包内可执行：

```bash
python tools/validate_project.py .
```

GitHub 文本源码仓库中不包含全部 PNG，使用：

```bash
python source/miband10pro/tools/validate_project.py source/miband10pro/project --source-only
```

## 生成 app.json

只有在确认 Smart Band 10 Pro 的真实 `deviceSource` 后才生成正式配置：

```bash
python tools/build_app_json.py \
  device/app.json.example \
  device/app.json \
  --platform-name "Xiaomi Smart Band 10 Pro" \
  --device-source VERIFIED_INTEGER \
  --design-width 400 \
  --release
```

不要使用猜测值替代 `VERIFIED_INTEGER`。

## EasyFace 研究结论

EasyFace Compiler v4.22 的发布说明写明加入了普通 Mi Band 10 支持，但没有明确写 Smart Band 10 Pro。普通 Mi Band 10 配置不能直接改名当作 10 Pro 配置。

## v0.5.0 静态检查

- `app.js` JavaScript 语法检查通过。
- `watchface/default-target/index.js` JavaScript 语法检查通过。
- 运行时必需的 57 个 PNG 素材全部通过格式验证。
- 完整开发包内 157 个 PNG 素材全部通过格式验证。
- `tools/build_app_json.py` 已通过临时配置生成测试。
- 完整开发包 SHA-256：`dcf239a7ac00a581ef5dbece9535b3ccc251076d56ca269cc9f448212b4cb5ce`。

## 仍然缺少

- 可确认的 Smart Band 10 Pro 平台或设备 ID。
- 可确认的编译器配置与安装包格式。
- 模拟器或真机安装测试。
- 最终安全区域和圆角参数。
- AOD 与锁屏验证。
- 月相与更多状态图标接入。

当前目录是开发源码，不是可安装 Release。
