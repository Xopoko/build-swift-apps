# Firmware Download & Extraction Reference

Complete reference for downloading and extracting Apple firmware with ipsw.

## Which Download Command Do I Need?

```
What do you want to download?
│
├─► iOS/iPadOS/tvOS/watchOS firmware
│   │
│   ├─► Full restore image (.ipsw file)
│   │   └─► ipsw download ipsw
│   │
│   ├─► Over-the-air update (smaller, delta updates)
│   │   └─► ipsw download ota
│   │
│   └─► Just the kernel or dyld_shared_cache (fastest)
│       └─► ipsw download ipsw --kernel --dyld
│           (extracts during download, no full IPSW saved)
│
├─► macOS installer
│   └─► ipsw download macos
│
├─► Kernel Development Kit (debug symbols, type info)
│   └─► ipsw download kdk
│
├─► Apple open source (xnu, dyld, etc.)
│   └─► ipsw download git <project>
│
├─► App Store IPA
│   └─► ipsw download ipa
│
├─► Firmware decryption keys
│   └─► ipsw download keys
│
└─► SHSH blobs / signing status
    └─► ipsw download tss
```

### Quick Decision Guide

| I want to... | Command |
|--------------|---------|
| Get latest iOS kernel for research | `ipsw download ipsw --device <ID> --latest --kernel` |
| Get dyld_shared_cache for class-dump | `ipsw download ipsw --device <ID> --latest --dyld` |
| Download full IPSW for restore | `ipsw download ipsw --device <ID> --latest` |
| Get beta/developer firmware | `ipsw download ota --device <ID> --beta` |
| Analyze macOS internals | `ipsw download macos --latest` |
| Get kernel debug symbols | `ipsw download kdk --latest` |
| Read xnu source code | `ipsw download git xnu` |
| Check if firmware is still signed | `ipsw download tss --device <ID> --build <BUILD>` |

### IPSW vs OTA: When to Use Which

| Criteria | `download ipsw` | `download ota` |
|----------|-----------------|----------------|
| File size | Larger (full image) | Smaller (delta) |
| Contains full filesystem | Yes | Partial |
| Best for kernel extraction | Yes | Yes |
| Best for dyld_shared_cache | Yes | Yes |
| Beta/seed releases | Limited | Yes (`--beta`) |
| Restore device | Yes | No |

---

## Table of Contents
- [IPSW Downloads](#ipsw-downloads)
- [OTA Downloads](#ota-downloads)
- [Remote Extraction](#remote-extraction)
- [Local Extraction](#local-extraction)
- [Kernel Development Kits](#kernel-development-kits)
- [macOS Downloads](#macos-downloads)
- [Other Downloads](#other-downloads)

---

## IPSW Downloads

Resolve the latest available iPhone device identifier before using these examples. Prefer the newest iPhone family and latest iOS release available from live data; if lookup is unavailable, ask for the intended target family/version before running commands.

```bash
LATEST_IPHONE_DEVICE="<latest-iPhone-device-identifier>"
LATEST_IPSW="<downloaded-latest-restore.ipsw>"
IOS_VERSION="<target-ios-version>"
BUILD_NUMBER="<target-build-number>"
OLDER_IOS_VERSION="<older-ios-version>"
NEWER_IOS_VERSION="<newer-ios-version>"
ADDITIONAL_DEVICE="<additional-device-identifier>"
```

**Download latest IPSW for device:**
```bash
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --latest
```

**Download specific iOS version:**
```bash
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --version "$IOS_VERSION"
```

**Download specific build:**
```bash
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --build "$BUILD_NUMBER"
```

**Download all IPSWs for a version:**
```bash
ipsw download ipsw --version "$IOS_VERSION"
```

**Download with kernel extraction:**
```bash
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --latest --kernel
```

**Download with dyld_shared_cache extraction:**
```bash
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --latest --dyld --dyld-arch arm64e
```

**Get download URLs only (no download):**
```bash
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --latest --urls
```

**Resume interrupted download:**
```bash
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --latest --resume-all
```

**Filter by device family:**
```bash
ipsw download ipsw --version "$IOS_VERSION" --white-list iPhone
ipsw download ipsw --version "$IOS_VERSION" --black-list iPad
```

---

## OTA Downloads

**Download latest OTA:**
```bash
ipsw download ota --platform ios --device "$LATEST_IPHONE_DEVICE" --latest
```

**Download with kernel extraction:**
```bash
ipsw download ota --platform ios --device "$LATEST_IPHONE_DEVICE" --kernel
```

**Download with dyld_shared_cache:**
```bash
ipsw download ota --platform ios --device "$LATEST_IPHONE_DEVICE" --dyld
```

**Beta/seed OTAs:**
```bash
ipsw download ota --platform ios --device "$LATEST_IPHONE_DEVICE" --beta
```

---

## Remote Extraction

Extract components from remote IPSW/OTA without downloading entire file.

**Extract kernel remotely:**
```bash
ipsw extract --kernel --remote https://updates.cdn-apple.com/path/to/ipsw
```

**Extract dyld_shared_cache remotely:**
```bash
ipsw extract --dyld --dyld-arch arm64e --remote https://updates.cdn-apple.com/path/to/ipsw
```

**Extract files matching pattern remotely:**
```bash
ipsw extract --files --pattern '.*\.plist$' --remote https://url/to/ipsw
```

**Get IPSW URL then extract:**
```bash
# Get URL
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --latest --urls

# Extract from URL
ipsw extract --kernel --remote <URL_FROM_ABOVE>
```

---

## Local Extraction

**Extract kernel:**
```bash
ipsw extract --kernel "$LATEST_IPSW"
```

**Extract dyld_shared_cache:**
```bash
ipsw extract --dyld --dyld-arch arm64e "$LATEST_IPSW"
```

**Extract both kernel and dyld:**
```bash
ipsw extract --kernel --dyld "$LATEST_IPSW"
```

**Extract DeviceTree:**
```bash
ipsw extract --dtree "$LATEST_IPSW"
```

**Extract iBoot:**
```bash
ipsw extract --iboot "$LATEST_IPSW"
```

**Extract SEP firmware:**
```bash
ipsw extract --sep "$LATEST_IPSW"
```

**Extract files by pattern:**
```bash
ipsw extract --files --pattern '.*Info\.plist$' "$LATEST_IPSW"
```

**Extract to specific directory:**
```bash
ipsw extract --kernel --output ./extracted/ "$LATEST_IPSW"
```

**Get system version info:**
```bash
ipsw extract --sys-ver "$LATEST_IPSW"
```

**JSON output:**
```bash
ipsw extract --kernel --json "$LATEST_IPSW"
```

---

## Kernel Development Kits

KDKs contain debug symbols and type information for kernel analysis.

**List available KDKs:**
```bash
ipsw download kdk --list
```

**Download specific KDK:**
```bash
ipsw download kdk --version 13.0
```

**Download latest KDK:**
```bash
ipsw download kdk --latest
```

After download, use with `ipsw ctfdump` for type analysis:
```bash
ipsw ctfdump /Library/Developer/KDKs/KDK_13.0/kernel.development task
```

---

## macOS Downloads

**Download macOS installer:**
```bash
ipsw download macos --version 14.0
```

**Download latest macOS:**
```bash
ipsw download macos --latest
```

**List available macOS versions:**
```bash
ipsw download macos --list
```

---

## Other Downloads

**Apple open source distributions:**
```bash
ipsw download git xnu
ipsw download git dyld
```

**Firmware keys from iPhone Wiki:**
```bash
ipsw download keys --device "$LATEST_IPHONE_DEVICE" --build "$BUILD_NUMBER"
```

**SHSH blobs / signing status:**
```bash
ipsw download tss --device "$LATEST_IPHONE_DEVICE" --build "$BUILD_NUMBER"
```

**App Store IPAs (requires auth):**
```bash
ipsw download ipa --bundle-id com.example.app
```

---

## Device Identifiers

Resolve identifiers from live data instead of copying stale examples. Prefer the newest iPhone family and latest iOS release available; if lookup is unavailable, ask for the intended target family/version.

**List all devices:**
```bash
ipsw device-list
```

**Get device info:**
```bash
ipsw device-info "$LATEST_IPHONE_DEVICE"
```

---

## Configuration

Create `~/.ipsw/config.yml` for persistent settings:

```yaml
download:
  resume-all: true
  output: ~/Downloads/ipsw
  proxy: http://proxy.example.com:8080
```

---

## Common Workflows

**Get kernel for latest iOS on the newest available iPhone:**
```bash
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --latest --kernel
```

**Build local firmware collection:**
```bash
for device in "$LATEST_IPHONE_DEVICE" "$ADDITIONAL_DEVICE"; do
    ipsw download ipsw --device $device --latest --kernel --dyld
done
```

**Compare kernels between versions:**
```bash
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --version "$OLDER_IOS_VERSION" --kernel
ipsw download ipsw --device "$LATEST_IPHONE_DEVICE" --version "$NEWER_IOS_VERSION" --kernel
ipsw kernel kexts --diff "kernelcache_$OLDER_IOS_VERSION" "kernelcache_$NEWER_IOS_VERSION"
```
