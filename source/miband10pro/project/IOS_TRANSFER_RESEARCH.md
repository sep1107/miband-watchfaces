# iPhone transfer research for P67

## Current status

An iPhone route is plausible, but it is **not yet verified on Xiaomi Smart Band 10 Pro / M2551B1**.

Two independent implementations provide useful evidence:

- the open-source My Band iOS project implements Xiaomi authentication, watchface install commands and chunked watchface upload with CoreBluetooth;
- Gadgetbridge has a dedicated Xiaomi Smart Band 10 Pro coordinator and exposes Xiaomi watchface management through its common service stack.

Neither source proves that the P67 device accepts a custom watchface from iOS. My Band currently documents hardware validation for the ordinary Smart Band 10, while watchface installation is still marked as awaiting confirmation. Gadgetbridge marks the 10 Pro coordinator as experimental.

## Important transport uncertainty

The My Band implementation uses CoreBluetooth and Xiaomi's BLE command/data channel.

Gadgetbridge currently labels both Smart Band 10 and Smart Band 10 Pro coordinators as `BT_CLASSIC`. Its `ConnectionType` enum defines that value as classic Bluetooth enabled and BLE disabled. At the same time, the shared Xiaomi coordinator still inherits the BLE coordinator, defines FE95 scan filters and uses the common Xiaomi service stack. This contradiction is consistent with experimental support and is not enough to decide the iPhone path without measuring the physical P67 device.

The unresolved question is therefore narrow:

> Does M2551B1 expose the authenticated watchface command and data-upload channel through BLE/GATT on iPhone, or is an Android-only classic Bluetooth transport required?

Until this is measured on the physical device, the project must not describe iPhone installation as supported.

## Safe validation sequence

Validation should advance without sending a custom watchface first:

1. **Advertisement only** — confirm that iPhone sees the P67 device name and advertised service UUIDs.
2. **Service discovery** — connect without an AuthKey and record whether FE95 plus characteristics 005E and 005F are visible.
3. **Authenticated BLE connection** — only after service discovery succeeds, confirm that the existing 16-byte Xiaomi AuthKey can establish the session.
4. **Read-only watchface list** — send only the encrypted list command and verify that the band responds.
5. **Official-file transfer probe** — only after the read-only path works, test the transfer framing with an already accepted official `resource.bin`; do not activate or delete anything automatically.
6. **Generated probe** — attempt the minimal generated P67 face only after the official-file path and recovery procedure are proven.

## Implemented discovery-only probe

`ios-probe/P67ReadOnlyProbe.swift` now implements stages 1 and 2 only. It:

- scans without a service filter and accepts only names beginning with `Xiaomi Smart Band 10 Pro`;
- records advertised service UUIDs;
- connects and discovers FE95;
- discovers 005E and 005F and records their CoreBluetooth properties;
- exports the result as JSON;
- disconnects immediately after discovery.

It intentionally contains no authentication, notification subscription, characteristic write, upload, activation or deletion code. The existing Python regression test scans the Swift source for required discovery calls and rejects known write/upload APIs, so a future change cannot silently turn the first probe into an installer.

The probe has passed local static safety checks and is committed, but it has **not yet been compiled in Xcode or run on the user's physical iPhone and M2551B1**.

## iPhone-side requirements

A physical iPhone and an Xcode-signed app are required for the first test. The existing My Band project is a likely host because it already implements Xiaomi authentication and upload, but the discovery-only probe can also be placed in a tiny standalone Xcode project.

The user does not need to install or build anything yet. Before requesting a device test, the next implementation task is to add a minimal SwiftUI report screen and verify that the probe compiles without bringing any upload service into the target.

## Current project guarantees

The repository can already:

- generate a structurally valid P67 `resource.bin` from scratch;
- validate Gadgetbridge-compatible magic, numeric ID, preview offset and normal or localized name metadata;
- create Xiaomi watchface upload envelopes with MD5, CRC32 and ordered chunks;
- reverse-inspect the generated binary and transfer payload;
- perform a discovery-only iPhone scan/service probe guarded against write and upload APIs.

These are static and protocol-level guarantees only. Physical-device acceptance remains unverified.
