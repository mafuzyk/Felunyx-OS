# Phase 2 Session Notes — 2026-08-06 (live-boot failure investigation)

**Branch:** `fix/phase-2-live-initrd-paths` — draft PR #9, based on `fix/phase-2-virtual-gate-build` (`fb2d745`).

This file records one working session. It is evidence of what was done and what remains; it is not a status update and does not change decisions.

## Context

The Phase 2 ISO from trusted build run `31030910170` booted in QEMU/OVMF only as far as `systemd-boot`, then reported `Error preparing initrd: Not Found` and fell through to PXE. The Virtual gate therefore cannot use that artifact.

## Root cause

- The live boot entries under `iso/profile/efiboot/loader/entries/` and `iso/profile/syslinux/syslinux.cfg` referenced `amd-ucode.img` and `intel-ucode.img` as separate initrd payloads.
- `mkarchiso` v89 only emits external microcode images when the initramfs does not already embed microcode. The Felunyx initramfs embeds microcode through its `microcode` hook, so those images are never produced in the final image.
- Result: `systemd-boot` aborts the entry (`Error preparing initrd: Not Found`) and the firmware falls through to PXE. PXE is a symptom, not the defect.
- Confirmed against the locked `releng` v89 profile and by read-only inspection of the artifact: `felunyx/boot/x86_64/` contains only `vmlinuz-*` and `initramfs-*.img`.

## Changes in PR #9 (draft, not merged)

1. `test: validate EFI boot payload paths` — new fail-closed validator contract; fails against the broken ISO.
2. `fix: align live initrd paths with archiso output` — entries now reference only kernel + initramfs; `tools/felunyx-validate` gained an EFI/syslinux payload path check.
3. `docs: record Phase 2 boot failure and validation` — defect note in the Phase 2 status document.

## Validation state

- **Remote (R):** 136 tests pass locally (134 before + 2 new); `actionlint` passes on all workflows; `make validate` only trips on local shellcheck 0.11 style-level findings that the CI shellcheck 0.9 does not emit (identical failure on base `fb2d745`, not a regression).
- **CI:** no Validate/Build runs appeared on PR #9 by end of session (GitHub Actions queue); the CI gates are still pending.
- **Build/Virtual (V):** a local frozen build was started twice; both attempts ended without an ISO (once on a temporary TMPDIR permission issue, once killed at the user's request). No new ISO was produced. The corrected ISO and its UEFI boot remain to be validated.

## Remaining work

- Confirm CI Validate + Build on PR #9 (or dispatch `workflow_dispatch`).
- Produce a corrected ISO (CI artifact or a later local frozen build with `TMPDIR` on the data disk).
- Run `felunyx-validate` against the new ISO and boot it in QEMU/OVMF (Virtual evidence), then update the status document and the Virtual gate evidence.
- No merge, no retarget, no force-push: PR #9 stays draft until reviewed.
