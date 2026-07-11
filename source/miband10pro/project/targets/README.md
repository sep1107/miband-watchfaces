# Target profiles

Target profiles control canvas geometry only. They do not prove firmware compatibility.

## Evidence fields

Every profile separates:

- `evidence.hardware`: confidence in the physical screen/canvas.
- `evidence.buildChain`: confidence in a related compiler or editor path.
- `evidence.deviceTarget`: confidence that Smart Band 10 Pro accepts the output.

## Profiles

| Profile | Canvas | Status | Hardware | Build chain | 10 Pro target |
| --- | --- | --- | --- | --- | --- |
| `compat-336x480` | 336×480 | reference build chain | indirect | tested on related Pro devices | reference only |
| `experimental-400x480` | 400×480 | reported hardware | reported | none | unverified |

## Commands

Validate all profiles:

```bash
python ../../tools/validate_target_profiles.py .
```

Apply one profile to the project:

```bash
python ../../tools/apply_target_profile.py .. compat-336x480.json
python ../../tools/apply_target_profile.py .. experimental-400x480.json
```

After applying a profile, run:

```bash
python ../../tools/validate_project.py ..
```

A profile may only use `status: verified-build-target` after a reproducible build and Smart Band 10 Pro installation are confirmed.
