# MiCreate Pro format probe

A real-device-tested Mi Band 9 Pro project shows that MiCreate project files are XML documents.

Observed reference header:

```xml
<FaceProject DeviceType="11" Id="161234567">
  <Screen Title="..." Bitmap="example.png">
```

The reference project's author states that this MiCreate version builds using the Mi Band 8 Pro target and that the resulting `.face` files work on Mi Band 9 Pro. This does **not** prove that `DeviceType="11"` is valid for Smart Band 10 Pro.

## Widget types observed

- `Shape="30"`: static image.
- `Shape="31"`: indexed image list driven by `Index_Src`.
- `Shape="32"`: numeric image list driven by `Value_Src`.

## Reference source IDs

| Data | Source ID |
| --- | ---: |
| Hour tens | 1000911 |
| Hour ones | 911 |
| Minute tens | 1211 |
| Minute ones | 1111 |
| Year | 812 |
| Month | 1012 |
| Day | 1812 |
| Weekday | 2012 |
| Steps | 821 |
| Heart rate | 822 |
| Battery | 841 |
| Weather icon | 3031 |
| Weather high | 1832 |
| Weather low | 2032 |

These IDs are format observations from the reference project, not an official Xiaomi specification.

## Generate the probe

```bash
python tools/build_micreate_probe.py \
  project/device/assets \
  micreate-probe \
  --accept-reference-device-type
```

The output contains a `.fprj` project and an adjacent `images/` directory. Open it in MiCreate on Windows. Do not distribute its output as a Smart Band 10 Pro build until the correct 10 Pro DeviceType is verified.
