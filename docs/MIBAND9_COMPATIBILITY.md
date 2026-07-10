# Mi Band 9 compatibility check

## Result

`miband9.bin` is currently **unverified** and should not be treated as a confirmed Mi Band 9 build.

## What was checked

- The former `watchfaces/miband7.bin` and `watchfaces/miband9.bin` files had the same Git blob SHA: `4237d1332a667160ffb47d4a0255aeccf81c0c8f`.
- The package SHA-256 is `8caf6df2d77a6829545ddfbe3ec6ff8f9e380e2bfebdaeb76dcb1a75352df1e4`.
- The package is a ZIP-based Zepp OS watchface package containing:
  - `app.json`
  - `app.bin`
  - `watchface/index.bin`
  - image resources
- The bundled `app.json` targets the older `gts` / `nxp` environment and does not contain a Mi Band 9 platform or device identifier.
- The visual resources use a 192 x 490 canvas, which matches the Mi Band 9 display resolution, but matching resolution alone does not prove package compatibility.

## Why installation cannot be confirmed

The executable parts (`app.bin` and `watchface/index.bin`) are already compiled for the original target. A filename change does not retarget those binaries to Mi Band 9 firmware.

Without one of the following, successful installation and runtime behavior cannot be verified:

1. A Mi Band 9 device test.
2. A Mi Band 9-capable emulator that validates the exact package format.
3. Rebuilding the watchface with a compiler profile and device identifiers intended for Mi Band 9.

## Status labels

- `miband7.bin`: original build.
- `miband9.bin`: byte-identical experimental copy; unverified on device.

## Recommendation

Do not advertise `miband9.bin` as a confirmed compatible release. Keep it marked as experimental until it is rebuilt with a Mi Band 9 target or tested on real hardware.
