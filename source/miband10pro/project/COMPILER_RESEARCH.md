# Compiler research

## EasyFace

The latest EasyFace release checked for this project is **EasyFace Compiler v4.22**, published on **2026-07-08**.

Its release note says:

```text
Mi Band 10 Support added
```

Source: https://github.com/m0tral/EasyFace/releases/tag/v4.22

## What this confirms

- EasyFace now has an explicit compiler path for the standard Mi Band 10.
- The project is no longer blocked by a complete absence of Mi Band 10 tooling.

## What it does not confirm

- The release note does not explicitly mention Xiaomi Smart Band 10 Pro.
- No verified Smart Band 10 Pro `deviceSource`, screen orientation, compiler profile, or package identifier has been found in public source files.
- A standard Mi Band 10 build must not be relabeled as a 10 Pro build without verification.

## Next compiler test

Once the EasyFace v4.22 compiler assets are available on a Windows environment:

1. Import or reconstruct the project using the Mi Band 10 target.
2. Inspect the generated target configuration and package metadata.
3. Compare its canvas and device identifiers against a known Smart Band 10 Pro watchface package.
4. Only generate `app.json` with `tools/build_app_json.py` after the target values are verified.
