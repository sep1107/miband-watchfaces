# Compiler research

## Verified P67 path

The real M2551B1 package establishes the required output family:

```text
manifest semantics + indexed8/RLEReversed resources
    -> resource.bin with magic 0x1234A55A
    -> P67 BIN package
```

The capability protocol (`1.9.4`) and the protocol encoded in the observed binary header (`0.9.3`) are separate values.

## Public binary implementation reference

A public watchface implementation uses the same `0x1234A55A` magic and exposes structures for:

- file header and version fields;
- themes and record tables;
- layouts, images and image arrays;
- data items, slots and widgets;
- binary resource addresses and deduplication.

Reference:

```text
https://github.com/mokshjain-cmd/watchface-merged/tree/main/ZhouHaiWatchFace/WatchBin
```

This code is a research reference, not yet a proven P67 compiler. Its image encoding, record variants and package assembly must be compared byte-for-byte against the real P67 sample before use.

## Legacy tools

- EasyFace support for the standard Mi Band 10 does not establish Smart Band 10 Pro compatibility.
- MiCreate projects for Mi Band 8/9 Pro are related-device references only.
- The Zepp OS `app.json` project is retained solely as a visual prototype.

## Implementation plan

1. Parse the complete P67 header, theme tables and record tables.
2. Map manifest element types to binary record types.
3. Reproduce indexed8 palette conversion.
4. Reproduce `RLEReversed` image encoding.
5. Build a minimal one-theme package and compare structure with the official sample.
6. Test installation on M2551B1 only after static checks pass.
