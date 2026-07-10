# Mi Band 10 adaptation project

> The scaffold currently targets the Xiaomi Smart Band 10 display size: `212 × 520`.
>
> Xiaomi's official product range lists Band 10, Glimmer Edition and Ceramic Edition. A separate official model named “Mi Band 10 Plus” has not been confirmed, so the final platform ID and package profile must still be verified before building.

## Directory

```text
project/
├── README.md
├── ASSET_INVENTORY.md
└── device/
    ├── app.json.example
    ├── app.js
    ├── assets/
    │   └── README.md
    └── watchface/
        └── default-target/
            └── index.js

../tools/
└── prepare_assets.py
```

## Current scaffold features

- 212 × 520 layout coordinate system.
- TIME FLIES title.
- Current hour and minute.
- Current date.
- Step count.
- Last measured heart rate.
- Battery percentage.
- Chinese festival or solar-term text when supported by the device language and runtime.
- Sensor listeners and cleanup in `onDestroy()`.

## Asset work

The original TIME FLIES package contains 157 selected image resources. The files use TGA binary data even though their filenames end with `.png`.

`../tools/prepare_assets.py` can generate a provisional 212 × 520 resource set using ImageMagick. This is only a mechanical first pass; important digits and icons still need visual inspection and manual cleanup.

## Still missing before a real build

1. Verified Mi Band 10 compiler profile and `deviceSource` values.
2. Confirmation that the target firmware accepts the selected Zepp OS or EasyFace package format.
3. Final image-widget layout using the migrated TIME FLIES assets.
4. Simulator or real-device installation test.
5. AOD and lock-screen behavior verification.

The current project is source scaffolding, not an installable `.bin` release.
