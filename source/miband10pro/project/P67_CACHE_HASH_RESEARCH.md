# Mi Fitness cache-hash research

## Evidence boundary

The user-provided M2551B1 watchface export contains 55 archive entries, including `resource.bin`, `manifest.xml`, `description.xml`, `capability.json`, `uidmap.map`, previews and source images.

It contains no file named `hashcode`, no signature file and no textual checksum field. The opaque 32-hex directory component from the original Android cache path is intentionally not stored in this repository.

## Candidate hashes checked

The opaque cache key does not equal the common MD5 values calculated from the extracted package:

```text
resource.bin   1ffc1e9607fd73f429f3aa5b98964d2f
manifest.xml   fe7ab05cf0c5912a1958c4ca1e2162c5
description.xml f3031b6c10b0b710ea2ddfaa31b26bfa
capability.json 58ccc86d43642a5ea950d562636ff066
uidmap.map      7839aa6c5d92ae16ed83e61541e5fa6d
export ZIP      d96c462618111543e2aa81c425b2a9a9
```

It also does not equal MD5 of:

- the numeric package ID;
- the editor `_id` value from `description.xml`;
- straightforward concatenations of package ID, device type, resolution and version;
- sorted concatenations of extracted file contents, filenames or per-file hashes.

## Conclusion

The directory component is most likely external metadata, such as:

- a hash of the original download URL;
- a server-provided cache key;
- a database primary key or content-location identifier;
- a value calculated from metadata not included in the exported directory.

It is not evidence of a checksum required inside `resource.bin`.

Direct Xiaomi watchface upload sends the raw binary with its own full-file MD5 and transfer-envelope CRC32. Therefore the Mi Fitness cache key is no longer a blocker for the preferred installation path. Cache replacement remains a fallback research topic rather than the main deployment strategy.
