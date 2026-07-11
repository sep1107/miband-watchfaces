# M2551B1 / P67 real-device package baseline

This directory stores a sanitized metadata fixture derived from a Mi Fitness watchface cache exported for a physical Xiaomi Smart Band 10 Pro.

Verified device context:

```text
Marketing name: Xiaomi Smart Band 10 Pro / 小米手环10 Pro
Model: M2551B1
Device OS: Xiaomi HyperOS 3.101.030
Watchface target: P67
Watchface OS: vela
Canvas: 336x480
Resolution code: XMHD03
Packet type: BIN
Capability protocol: 1.9.4
```

The fixture contains only metadata needed for automated validation:

- `capability.json`
- `description.xml`
- a minimized `manifest.xml`
- `package-summary.json`

It does **not** contain Xiaomi artwork, the original `resource.bin`, account data, Bluetooth addresses, serial numbers, logs, or user photographs.

The complete user-supplied cache export had SHA-256:

```text
e607efbaa564ff88a248374c1b19261debca974c6a39993cc8c4d06c222a2049
```

Its `resource.bin` had SHA-256:

```text
a3c1f2e59346117b2885bd06a36a358b525aeaa70ecad8c7e51bf6ac00fc9669
```

The package proves the official target and canvas. It does not yet prove that a custom-generated BIN is accepted by the device.
