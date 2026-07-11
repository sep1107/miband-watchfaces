# Target profiles

The Smart Band 10 Pro workspace uses one verified official-package target:

| Profile | Canvas | Device type | Watch OS | Packet | Status |
| --- | --- | --- | --- | --- | --- |
| `p67-336x480` | 336×480 | `P67` | `vela` | `BIN` | official package verified |

`compat-336x480` is retained only as a historical Mi Band 8/9 Pro build-chain reference. It is not an active Smart Band 10 Pro compiler target.

## Evidence boundary

The official package proves the target metadata and canvas. It does not yet prove that a newly generated custom BIN will be accepted by the physical device.

## Commands

Validate all profiles:

```bash
python ../../tools/validate_target_profiles.py .
```

Rebuild the verified profile from the sanitized Mi Fitness fixture:

```bash
python ../../tools/extract_p67_profile.py \
  ../../reference/real-device/P67-baseline \
  --profile-out /tmp/p67-336x480.json \
  --report-json /tmp/p67-report.json \
  --report-markdown /tmp/p67-report.md
```

Apply the verified geometry to the legacy visual prototype:

```bash
python ../../tools/apply_target_profile.py .. p67-336x480.json
```
