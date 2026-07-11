# P67 `resource.bin` binary format notes

## Scope

These notes are derived from the user-provided Mi Fitness cache package for a physical Xiaomi Smart Band 10 Pro (`M2551B1`) and from structural comparison with a public watchface implementation.

The original Xiaomi binary and artwork are not committed. Only offsets, sizes, counts, hashes and other non-sensitive derived facts are recorded.

## Verified file layout

The real sample uses binary protocol `0.9.3` and has this high-level layout:

```text
0x0000  Header                    168 bytes
0x00A8  Theme 0                  176 bytes
0x0158  Theme 1                  176 bytes
0x0208  Theme 2                  176 bytes
0x02B8  RecordBase area         3648 bytes
0x10F8  Raw payload area      246506 bytes
```

Decimal offsets:

```text
Header size:       168
Theme size:        176
Theme count:         3
Record area:       696
Raw-data area:    4344
File size:      250850
```

All 228 record entries and their payload ranges fit inside the file. UID record types match their containing tables with zero structural validation errors.

## Header — 168 bytes

| Offset | Size | Field | Verified sample |
| ---: | ---: | --- | --- |
| 0 | 4 | Magic, little-endian | `0x1234A55A` |
| 4 | 4 | Watchface version | `1.0.12` |
| 8 | 4 | Editor version | `0.0.0` |
| 12 | 4 | Generator version | `0.0.0` |
| 16 | 4 | Binary protocol | `0.9.3` |
| 20 | 4 | Firmware version | `1.0.0` |
| 24 | 1 | Color-group count | `0` |
| 25 | 3 | Reserved | zero |
| 28 | 1 | Theme count | `3` |
| 29 | 1 | Color count | `0` |
| 30 | 2 | Flags | `0x0002` |
| 32 | 4 | Default preview address | `5465` |
| 36 | 4 | Reserved word | `0` |
| 40 | 64 | Package ID | `120917384229` |
| 104 | 64 | Name/reserved area | starts with `0xFFFFFFFF` in this sample |

The public implementation at commit `c808d39e07c88f84e3f5305c1557ffcc481fe352` also defines the 168-byte header layout:

```text
https://github.com/mokshjain-cmd/watchface-merged/blob/c808d39e07c88f84e3f5305c1557ffcc481fe352/ZhouHaiWatchFace/WatchBin/Model/BinFileHeader.cs
```

## P67 Theme entry — 176 bytes

The public implementation models an 88-byte Theme core. The real P67 sample contains an additional 88-byte extension after every core, making each Theme entry 176 bytes.

### Theme core — 88 bytes

| Offset in Theme | Size | Field |
| ---: | ---: | --- |
| 0 | 4 | Background UID |
| 4 | 4 | Preview-image address |
| 8 | 80 | Ten `{recordCount, recordAddress}` pairs |

Each pair is 8 bytes and corresponds to record types `0` through `9`.

### P67 extension — 88 bytes

| Offset in extension | Size | Observed value |
| ---: | ---: | --- |
| 0 | 4 | unknown word, `0` in all three themes |
| 4 | 4 | boundary-like address: `1912`, `3128`, `4344` |
| 8 | 4 | unknown word, `0` in all three themes |
| 12 | 4 | same boundary-like address |
| 16 | 64 | UTF-8 style name: `样式1`, `样式2`, `样式3` |
| 80 | 8 | reserved zero bytes |

The address words line up with the end of each theme's RecordBase block. Their semantic names are not yet proven, so the parser exposes them as raw `words` rather than assigning speculative labels.

## RecordBase — 16 bytes

| Offset | Size | Field |
| ---: | ---: | --- |
| 0 | 4 | UID |
| 4 | 4 | Flags |
| 8 | 4 | Payload address |
| 12 | 4 | Payload length |

The UID high byte is the record type. The lower 24 bits are retained as the record index.

Public structural reference:

```text
https://github.com/mokshjain-cmd/watchface-merged/blob/c808d39e07c88f84e3f5305c1557ffcc481fe352/ZhouHaiWatchFace/WatchBin/Model/RecordBase.cs
```

## Verified record tables

Counts across all three themes:

| Type | Name | Count |
| ---: | --- | ---: |
| 0 | Layout | 60 |
| 2 | Image | 45 |
| 3 | ImageArray | 27 |
| 6 | Translation | 9 |
| 7 | Data | 48 |
| 8 | Slot | 3 |
| 9 | Widget | 36 |
|  | **Total** | **228** |

Each theme contains:

```text
Layout:       20
Image:        15
ImageArray:    9
Translation:   3
Data:         16
Slot:          1
Widget:       12
Total:        76
```

## Partially decoded payload headers

`tools/inspect_p67_binary.py` currently decodes these safe structural fields:

- Layout: referenced UID, x, y and parameter word.
- Image: format, flags, compression selector, width, height and encoded length.
- ImageArray: format, image count, flags, dimensions and encoded length.
- Data: source ID.
- Slot: widget count and flags.
- Widget: name, background UID, preview UID, record count, group type and flags.

The parser does not extract, reconstruct or commit official artwork.

## Tooling

Inspect a locally available real binary:

```bash
python tools/inspect_p67_binary.py resource.bin \
  --json p67-binary-report.json \
  --markdown p67-binary-report.md
```

CI uses a synthetic binary fixture to verify:

- 168-byte Header;
- 176-byte extended Theme entry;
- 16-byte RecordBase;
- style-name decoding;
- record and payload address handling.

## Remaining unknowns

1. Exact semantics of the four extension words.
2. Complete Translation payload layout.
3. Complete Data, Slot and Widget optional fields.
4. Exact indexed8 palette representation.
5. Exact `RLEReversed` encoding and alignment rules.
6. Package assembly and integrity rules required for installation.

A custom BIN must not be tested on the physical device until all generated addresses, lengths and image bounds pass static validation.
