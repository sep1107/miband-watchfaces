# P67 probe package scaffold

## Status

The repository can now generate a complete watchface-package directory and ZIP scaffold from scratch for the verified Xiaomi Smart Band 10 Pro target:

```text
M2551B1 / P67 / vela / 336x480 / XMHD03 / BIN
```

This is a **structural probe**, not yet a device-verified installable watchface.

## Generated package contents

`tools/p67_probe_package.py` produces:

```text
capability.json
description.xml
manifest.xml
uidmap.map
resource.bin
preview/aod-preview.png
preview/market-preview.png
preview/preview.png
preview/style_1_static.png
resources/_preview/probe.png
resources/probe.png
```

The package uses a new numeric package ID and contains only generated artwork. It does not redistribute Xiaomi artwork or the user's original `resource.bin`.

## Verified relationships

The generator and regression tests verify:

- `description.xml` declares `P67`, `vela`, `336x480`, `indexed8` and compressed images;
- `capability.json` declares `XMHD03`, `CN`, protocol `1.9.4` and packet type `BIN`;
- `manifest.xml` declares `RLEReversed`, one theme, one preview image and one display image;
- preview-only `Image1` is not emitted as a RecordBase entry;
- visible `Image2` maps to UID `0x02000001`, matching the real-device package numbering convention;
- `uidmap.map`, the layout payload and the image RecordBase agree on that UID;
- `resource.bin` contains a 168-byte header, one 176-byte P67 theme entry, one layout record and one image record;
- both preview and display image records decode to the generated 336x480 indexed8 image;
- all internal offsets and lengths remain within the file and the final file is four-byte aligned;
- the complete directory can be archived as a valid ZIP without adding host-specific paths.

## Tools

```text
tools/p67_minimal_builder.py
tools/test_p67_minimal_builder.py
tools/p67_probe_package.py
tools/test_p67_probe_package.py
```

GitHub Actions generates the minimal `resource.bin`, reverse-inspects it, generates the complete package scaffold and checks the resulting ZIP on every relevant change.

## Remaining uncertainty

Static structure alone does not prove that Mi Fitness or the physical M2551B1 will accept the package. The following may still be required:

- an external package hash or signature;
- additional cache metadata stored outside the exported directory;
- a store-assigned package identity;
- exact semantics for currently unnamed P67 theme-extension fields;
- a different import/transfer path than replacing a cached package;
- firmware-side validation that is not represented in the package files.

No package should be described as installable until the complete transfer path is understood and a controlled test succeeds on the physical device.

## Next milestone

1. Compare multiple real P67 package directories to identify fields that vary per package and fields that are generated externally.
2. Trace how Mi Fitness verifies `resource.bin` and selects a cached watchface directory.
3. Determine whether the missing `hashcode` observed in some directory listings is a separate file, database value or server response.
4. Only then prepare a controlled device test with a unique package ID and a recovery plan.
