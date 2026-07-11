# P67 direct watchface transfer path

## Status

A raw P67 `resource.bin` can be framed for Xiaomi's watchface upload service without using a Mi Fitness cache directory or ZIP package.

The protocol is implemented by `tools/p67_transfer_protocol.py` and covered by deterministic regression tests. The framing has been cross-checked against two independent open-source implementations:

- Gadgetbridge: `XiaomiWatchfaceService.java` and `XiaomiDataUploadService.java`;
- My Band: `WatchfaceService.swift`, `DataUploadService.swift` and `InstallableFile.swift`.

The transport sequence is verified in software, but it has not yet been exercised on the physical M2551B1.

## Raw watchface identity

The file sent to the band is the raw binary, not the package ZIP.

```text
uint32 little-endian magic at 0x00 = 0x1234A55A
NUL-terminated numeric package ID at 0x28
optional NUL-terminated name at 0x68
```

The real-device sample and the generated probe both satisfy these rules.

## Command sequence

1. Send an encrypted watchface-install announcement:

```text
command type    = 4
subtype         = 4
watchface ID    = numeric string from offset 0x28
size            = full resource.bin length
```

2. Wait for watchface install status `0`.

3. Send an encrypted data-upload request:

```text
command type    = 22
subtype         = 0
upload type     = 16
md5             = MD5 of the full resource.bin, 16 raw bytes
size            = full resource.bin length
```

4. Read the upload acknowledgement. It supplies a status, resume position and optional chunk size. The established implementations use 2048 bytes when no chunk size is supplied.

5. Build the plaintext data-channel payload:

```text
byte    0x00
byte    upload type = 16
byte[16] MD5 of full resource.bin
uint32  full file size, little-endian
byte[]  resource.bin bytes starting at resume position
uint32  CRC32 of every preceding envelope byte, little-endian
```

6. Split the payload into chunks. Four bytes of every chunk are reserved for the chunk header:

```text
uint16 total parts, little-endian
uint16 current part, little-endian and 1-based
byte[] payload slice of at most chunkSize - 4 bytes
```

7. After upload completion, activate the face with watchface command type `4`, subtype `1`, using the same numeric ID.

## Verified local results

For the real M2551B1 cache sample:

```text
package ID: 120917384229
resource.bin size: 250850 bytes
resource.bin MD5: 1ffc1e9607fd73f429f3aa5b98964d2f
upload payload size: 250876 bytes
chunks at 2048-byte negotiated size: 123
```

The generated minimal probe also passes:

- raw-header identity inspection;
- MD5 envelope verification;
- CRC32 verification;
- chunk splitting and ordered reassembly;
- reverse parsing after generation.

## Cache-hash consequence

The Mi Fitness cache directory's opaque hash is not present in the BLE upload envelope. It may be a URL, database or download-cache key, but it is not required by the direct transfer framing described above.

This means cache replacement is no longer the preferred installation route. Direct authenticated BLE upload is cleaner and avoids depending on Mi Fitness's private directory layout.

## Remaining uncertainty

- M2551B1 / P67 compatibility with the same Xiaomi command service numbers still needs a controlled device test.
- The phone must authenticate with the band and send encrypted command-channel messages before plaintext data chunks can be accepted.
- Firmware may reject structurally valid custom binaries after the initial announcement.
- A safe test must preserve an installed stock face and use a unique numeric package ID.

No generated watchface should be called device-installable until that controlled test succeeds.
