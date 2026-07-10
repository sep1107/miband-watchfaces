# Smart Band 10 Pro assets

这里是 TIME FLIES 的 10 Pro 图片资源目录说明。

## 暂定画布

```text
400 × 480
```

该画布只是当前开发参数，后续可以根据正式 SDK 或真机信息调整。

## 已完成的开发素材

已从原 TIME FLIES 包整理并转换 157 个资源：

- 背景：188 × 480，放在 400 × 480 画布左侧。
- 时间数字：64 × 97。
- 星期图片：48 × 25。
- 天气图标：48 × 48。
- 电量图：50 × 20。
- 其他状态、数据、星期、等级和月相资源按分组保持宽高比处理。

所有开发素材都已转换成真实的 32 位 RGBA PNG，并通过格式验证。

## 仓库与完整包

当前 GitHub 连接只能稳定写入文本源码，无法把 157 个二进制 PNG 逐项提交到这个目录。因此：

- GitHub 中保存布局源码、配置模板、生成工具和资源说明。
- 完整开发 ZIP 中包含 `device/assets/` 下的全部 157 个 PNG。
- 完整包 SHA-256：`a075881ccb1ef92fd7b554b3977af1b7feadf00771c470cfbca219c5f6e780ba`。

## 资源路径

源码使用以下目录：

```text
assets/bg/
assets/time/
assets/week/
assets/weather/
assets/battery/
assets/status/
assets/date/
assets/data/
assets/smdata/
assets/level/
assets/moon/
```

`../../tools/prepare_assets.py` 可用于重新生成其他画布或倍率的素材。
