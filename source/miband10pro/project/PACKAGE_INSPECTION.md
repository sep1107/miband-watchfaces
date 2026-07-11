# Watchface package inspection

`tools/inspect_watchface_package.py` prepares the project for the moment a real Smart Band 10 Pro package becomes available.

## Supported inputs

- ZIP-based `.bin` watchfaces.
- `.zpk` containers, including nested `device.zip` and `app-side.zip` files.
- MiCreate `.fprj` and `.info` XML.
- `.face`, `.dat` and raw binary files through printable-string scanning.
- JSON configurations.
- PNG and TGA image headers, including TGA data stored with `.png` filenames.

## Reported evidence

- File size and SHA-256.
- Archive classification and entry list.
- Nested archive structure, up to three levels.
- Image formats and common dimensions.
- `deviceSource`, `DeviceType`, `DeviceVersion` and related identifiers.
- `designWidth`, width, height and resolution strings.
- Metadata lines mentioning Xiaomi, Mi Band, Smart Band, Amazfit, Zepp, HyperOS, EasyFace, MiCreate, `gts` or `nxp`.

## Usage

```bash
python tools/inspect_watchface_package.py package.face \
  --json package-report.json \
  --markdown package-report.md
```

## Current regression results

### Original TIME FLIES package

- Recognized as a ZIP-based compiled watchface package.
- 177 archive entries.
- 160 TGA images, despite `.png` filenames.
- Metadata includes `gts` and `nxp`.
- No 10 Pro device target was found.

### Amazfit Band 7 reference package

- Recognized as a Zepp OS package container.
- Recursively inspected two nested archives.
- Found `194x368` and `designWidth: 194`.
- Found `deviceSource` values `252`, `253` and `254`.

## Compatibility rule

The inspector reports metadata evidence only. A matching resolution, device name string or related-family package does not by itself prove Smart Band 10 Pro installation compatibility.
