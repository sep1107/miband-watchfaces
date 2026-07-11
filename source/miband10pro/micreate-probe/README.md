# MiCreate format probe

This directory stores a text-only MiCreate `.fprj` probe. It is a format experiment, not a Smart Band 10 Pro release.

- `TimeFlies_ProProbe.fprj` is valid XML.
- `DeviceType="11"` comes from a tested Mi Band 8/9 Pro reference project.
- The correct Smart Band 10 Pro DeviceType is still unknown.
- The complete downloadable probe package contains an adjacent `images/` directory with 69 PNG files and a 336 × 480 `example.png`.
- Battery images use 10% thresholds; weather temperatures include a minus-sign image.

The purpose is to test whether MiCreate can open and rebuild the TIME FLIES structure without presenting the reference target as verified 10 Pro compatibility.
