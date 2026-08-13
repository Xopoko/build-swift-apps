# Binary And Distribution Tool Cheat Sheet

Native Apple CLI utilities for Mach-O binary inspection and for the raw
`.pkg`/notarization command paths. Use them alongside the signing workflow in
`../SKILL.md`. For guided notarization submissions prefer
`appstore-notary-runner`; for distribution readiness review prefer
`macos-notarization-packager`.

## Mach-O Inspection

- `otool -L <binary>` — linked dylibs and frameworks. First stop for launch
  refusals caused by missing or unexpected dependencies.
- `otool -l <binary>` — load commands: rpaths, minimum OS, encryption info,
  and the `LC_CODE_SIGNATURE` segment.
- `otool -hv <binary>` — Mach header, file type, and flags.
- `nm -gU <binary>` — exported (defined external) symbols; `nm -u <binary>`
  for undefined symbols the binary expects at load time.
- `llvm-nm --demangle <binary>` — symbol listing with Swift/C++ demangling.
- `llvm-objdump --macho --all-headers <binary>` — LLVM view of headers and
  load commands; `llvm-objdump -d <binary>` to disassemble.
- `ar -t <lib.a>` — list members of a static archive; `libtool -static -o
  merged.a a.a b.a` to merge archives when a nested static-library slice is
  suspect.

Run LLVM tools through the active toolchain with `xcrun` (for example
`xcrun llvm-objdump ...`) so the version matches the selected Xcode.

## Symbols And Coverage

- `dsymutil <binary> -o App.dSYM` — link DWARF debug info into a dSYM for
  crash symbolication.
- `dsymutil --verify <binary>` — check debug-info integrity.
- `xcrun llvm-cov report <binary> -instr-profile=default.profdata` — coverage
  summary from an instrumented test run.

## Installer Packaging (.pkg)

- `pkgbuild --component App.app --install-location /Applications --identifier com.example.app --version 1.0 App.pkg`
  — component package from an app bundle.
- `productbuild --component App.app /Applications --sign "Developer ID Installer: <team>" Installer.pkg`
  — signed distribution package for the simple one-app case.
- `productbuild --distribution dist.xml --package-path . Installer.pkg`
  — distribution package driven by a distribution definition.
- Installers are signed with a Developer ID Installer certificate (`--sign` on
  either tool); the app bundle inside keeps its Developer ID Application
  signature. Do not conflate the two identities.

## Raw notarytool

Direct `xcrun notarytool` command path when the `asc notarization` wrapper is
unavailable:

- `xcrun notarytool store-credentials <profile> --apple-id <id> --team-id <team>`
  — one-time keychain profile setup (prompts for an app-specific password).
- `xcrun notarytool submit App.zip --keychain-profile <profile> --wait`
- `xcrun notarytool history --keychain-profile <profile>`
- `xcrun notarytool info <submission-id> --keychain-profile <profile>`
- `xcrun notarytool log <submission-id> --keychain-profile <profile> notary.json`
  — per-file issue details for rejected submissions.
- `xcrun stapler staple App.app` then `xcrun stapler validate App.app` after
  acceptance.
