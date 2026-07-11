# iPhone transfer research for P67

## Current status

An iPhone route is plausible, but it is **not yet verified on Xiaomi Smart Band 10 Pro / M2551B1**.

Two independent implementations provide useful evidence:

- the open-source My Band iOS project implements Xiaomi authentication, watchface install commands and chunked watchface upload with CoreBluetooth;
- Gadgetbridge has a dedicated Xiaomi Smart Band 10 Pro coordinator and exposes Xiaomi watchface management through its common service stack.

Neither source proves that the P67 device accepts a custom watchface from iOS. My Band currently documents hardware validation for the ordinary Smart Band 10, while watchface installation is still marked as awaiting confirmation. Gadgetbridge marks the 10 Pro coordinator as experimental.

## Important transport uncertainty

The My Band implementation uses CoreBluetooth and Xiaomi's BLE command/data channel.

Gadgetbridge currently labels both Smart Band 10 and Smart Band 10 Pro coordinators as `BT_CLASSIC`. That label may describe the preferred Android connection backend rather than prove that every command requires classic Bluetooth, because the shared Xiaomi stack also defines BLE scan filters and GATT services.

The unresolved question is therefore narrow:

> Does M2551B1 expose the authenticated watchface command and data-upload channel through BLE/GATT on iPhone, or is an Android-only classic Bluetooth transport required?

Until this is measured on the physical device, the project must not describe iPhone installation as supported.

## Safe validation sequence

Validation should advance without sending a custom watchface first:

1. **Advertisement only** — confirm that iPhone sees the P67 device name and advertised service UUIDs.
2. **Authenticated BLE connection** — confirm that the existing 16-byte Xiaomi AuthKey can establish the session.
3. **Service discovery** — record whether the Xiaomi service and command/data characteristics used by My Band are present.
4. **Read-only watchface list** — send only the encrypted list command and verify that the band responds.
5. **Official-file transfer probe** — only after the read-only path works, test the transfer framing with an already accepted official `resource.bin`; do not activate or delete anything automatically.
6. **Generated probe** — attempt the minimal generated P67 face only after the official-file path and recovery procedure are proven.

## iPhone-side requirements

The existing My Band project requires a physical iPhone, Xcode, an Apple signing identity and the device AuthKey. It is not currently distributed through the App Store.

The user does not need to install or build it yet. The next implementation task is to prepare a minimal P67-specific compatibility patch and a read-only diagnostic screen, so the first test cannot upload, activate or delete a face by accident.

## Current project guarantees

The repository can already:

- generate a structurally valid P67 `resource.bin` from scratch;
- validate Gadgetbridge-compatible magic, numeric ID, preview offset and normal or localized name metadata;
- create Xiaomi watchface upload envelopes with MD5, CRC32 and ordered chunks;
- reverse-inspect the generated binary and transfer payload.

These are static and protocol-level guarantees only. Physical-device acceptance remains unverified.
