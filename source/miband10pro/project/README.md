# TIME FLIES — Xiaomi Smart Band 10 Pro

## Provisional target

```text
Canvas: 400 × 480
Panel specification commonly reported as: 480 × 400
Screen: 1.74-inch AMOLED
```

The coordinate orientation is provisional. If the final compiler expects `480 × 400`, the constants and layout zones can be transposed without rewriting the sensor logic.

## Layout zones

```text
┌──────────────────────────────────────┐
│              TIME FLIES              │
├──────────────────────┬───────────────┤
│                      │ date          │
│      large time      │ steps         │
│                      │ heart rate    │
│                      │ battery       │
├──────────────────────┴───────────────┤
│ festival / solar term / status       │
└──────────────────────────────────────┘
```

## Implemented source features

- Current time and date.
- Step count.
- Last measured heart rate.
- Battery percentage.
- Chinese festival or solar-term text when supported.
- Sensor event listeners and cleanup.
- Constants for screen size, margins and column widths.

## Asset migration

The original TIME FLIES package uses TGA image data with `.png` filenames. The 10 Pro migration must preserve aspect ratio; direct `192 × 490` to `400 × 480` stretching is not acceptable.

The helper script in `../tools/prepare_assets.py` supports proportional scaling and background canvas expansion.

## Blocking items

- Verified Smart Band 10 Pro platform/device ID.
- Verified compiler profile and package format.
- Simulator or physical-device test.
- Final safe-area and corner-radius measurements.
- AOD and lock-screen validation.

This directory is development source, not an installable release.
