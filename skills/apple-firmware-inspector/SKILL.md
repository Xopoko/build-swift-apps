---
name: apple-firmware-inspector
description: "Apple firmware and binary reverse engineering with the `ipsw` CLI: IPSW/kernelcache download/extraction, dyld_shared_cache disassembly, private headers, entitlements, Mach-O analysis, Apple internals, KEXTs, and security research."
---

# Apple Firmware Inspector

Install: `brew install blacktop/tap/ipsw`.

When a device target is needed, resolve current identifiers with `ipsw device-list` or live data. Do not copy stale iPhone identifiers.

## Workflows

Firmware:

```bash
ipsw download ipsw --device "$DEVICE" --latest
ipsw download ipsw --device "$DEVICE" --latest --kernel --dyld
ipsw extract --kernel "$LATEST_IPSW"
ipsw extract --dyld --dyld-arch arm64e "$LATEST_IPSW"
ipsw extract --kernel --remote <IPSW_URL>
```

Userspace / dyld shared cache:

```bash
DSC=/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64e
ipsw dyld a2s "$DSC" 0xADDR
ipsw dyld symaddr "$DSC" "_symbol" --image Some.framework/Some
ipsw dyld disass "$DSC" --vaddr 0xADDR
ipsw dyld disass "$DSC" --symbol "_symbol" --image Some.framework/Some
ipsw dyld xref "$DSC" 0xADDR --all
ipsw dyld dump "$DSC" 0xADDR --size 256
ipsw dyld str "$DSC" "pattern" --image Some.framework/Some
ipsw dyld objc --class "$DSC" --image Some.framework/Some
ipsw dyld extract "$DSC" Some.framework/Some -o ./out/
```

Kernel/KEXT:

```bash
ipsw kernel kexts kernelcache.release.$DEVICE
ipsw kernel extract kernelcache sandbox --output ./kexts/
ipsw kernel syscall kernelcache
ipsw kernel kexts --diff "kernelcache_old" "kernelcache_new"
```

Entitlements:

```bash
ipsw macho info --ent /path/to/binary
ipsw ent --sqlite ent.db --ipsw "$LATEST_IPSW"
ipsw ent --sqlite ent.db --key "com.apple.private.security.no-sandbox"
```

Class dump:

```bash
ipsw class-dump "$DSC" SpringBoardServices --headers -o ./headers/
ipsw class-dump "$DSC" Security --class SecKey
ipsw class-dump "$DSC" UIKit --class 'UIApplication.*' --headers -o ./headers/
ipsw class-dump "$DSC" Security --re
```

Mach-O:

```bash
ipsw macho info /path/to/binary
ipsw macho disass /path/to/binary --symbol _main
ipsw macho info --sig /path/to/binary
```

## Tips

- First `a2s`/`symaddr` creates cache; later lookups are faster.
- Use `--image <DYLIB>` for DSC operations; it is much faster.
- Most commands support `--json` for scripting.

## References

- `references/download.md`
- `references/dyld.md`
- `references/kernel.md`
- `references/entitlements.md`
- `references/class-dump.md`
- `references/macho.md`
