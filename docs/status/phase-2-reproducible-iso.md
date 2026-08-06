# Phase 2 Status — Reproducible ISO Skeleton

**Last reviewed:** 2026-08-05

**Current conclusion:** the Phase 2 implementation exists, but the phase is not approved or merged. Source-level virtual-gate hardening has been validated remotely; the complete Remote and Virtual gates remain pending evidence and review.

## Goal

Produce a minimal, repeatable, virtually bootable and installable Felunyx OS skeleton with Linux Zen as the default, Linux LTS as an explicit fallback, a minimal Plasma Wayland live session, Calamares, Btrfs, and installed GRUB.

## Validation vocabulary

This document uses only the following validation-state terms:

- `implemented`: code or configuration exists, without implying runtime proof;
- `validated remotely`: source, schemas, tests, builds, manifests, or CI were checked remotely;
- `validated in VM`: the matching artifact executed successfully in a reviewed virtual-machine scenario;
- `validated in hardware`: the matching artifact executed successfully on reviewed physical hardware;
- `pending`: required work or evidence is incomplete;
- `not tested`: no evidence exists at that level.

A component marked `validated remotely` does not make the complete Remote gate pass. A Remote result does not imply `validated in VM`, and a VM result does not imply `validated in hardware`.

## Current state

| Scope | State | Evidence and limitation |
|---|---|---|
| Approved Phase 2 design and plan | implemented | `docs/superpowers/specs/2026-08-04-phase-2-reproducible-iso-design.md` and `docs/superpowers/plans/2026-08-04-phase-2-reproducible-iso.md` |
| Phase 2 ISO skeleton | implemented | PR #3, branch `agent/phase-2-implementation`, fixed review head `1f89d17b10c8e0b4965a7f8ebc5e4d509e5f637a`; the PR is draft and unmerged |
| Virtual-gate hardening Tasks 1–7 | validated remotely | PR #5, branch `fix/phase-2-virtual-gate-hardening`; validation run `31007003860` reported 132 tests passed |
| Remote gate | pending | One trusted development build exists, but the complete lock, provenance, checksum, manifest, two-build comparison evidence, and R1/R2/R3 review have not all been closed |
| Virtual gate | pending | Requires a matching rebuilt ISO, all required hardened scenarios, uploaded evidence, and human review of the results |
| Hardware gate | not tested | Physical USB, firmware, GPU, network, storage, power, peripherals, and multi-monitor checks remain in the H queue |
| Phase 3 implementation | pending | Phase 3 implementation remains blocked until the Phase 2 review boundary is explicitly approved |

## Branches and pull requests

### PR #3 — Phase 2 ISO skeleton

PR #3 contains the Phase 2 implementation on `agent/phase-2-implementation`. Its review baseline is commit `1f89d17b10c8e0b4965a7f8ebc5e4d509e5f637a`. It remains draft and unmerged; no merge or phase approval is implied by a successful build.

### PR #5 — Virtual-gate hardening

PR #5 is isolated on `fix/phase-2-virtual-gate-hardening` and targets the PR #3 branch rather than `main`. Tasks 1–7 strengthened live evidence, semantic Zen/LTS selection, installed-system inspection, GRUB one-shot selection, controlled installer failure, QEMU scenario records, and fail-closed workflow aggregation.

The source contracts reached `validated remotely` in validation run `31007003860`, where 132 tests passed. Those results validate source behavior and workflow policy only. They do not establish the complete Remote gate and do not count as `validated in VM`.

### PR #6 — Work Environments preparation

PR #6 is preparatory design only for a possible later phase. It is based on `main`, is not consumed by PR #5, and does not authorize Phase 3 implementation. Shared documentation such as `docs/README.md` must be reconciled explicitly after the Phase 2 boundary rather than overwritten from this branch.

## Existing development artifact

Trusted build workflow run `30951476281` produced the artifact:

- name: `felunyx-phase2-30951476281`;
- digest: `sha256:cf130079fdf93b1fd6a7deb2581135882fe9fdb2fcbf1bb2c77881087733cd10`;
- classification: internal development artifact;
- release status: not a release.

This artifact proves that one development build completed and was uploaded. It predates the guest-side hardening in PR #5, so it cannot inherit the new live, installed, GRUB, Calamares-failure, or workflow validation. It must not be used to claim that the hardened Virtual gate passed.

## Known boot defect in the second development artifact

The trusted build run `31030910170` produced an ISO that reaches `systemd-boot` but fails to boot with `Error preparing initrd: Not found` and falls through to PXE. Root cause: the live entries under `iso/profile/efiboot/loader/entries/` and `iso/profile/syslinux/syslinux.cfg` referenced external `amd-ucode.img` and `intel-ucode.img` payloads, but `mkarchiso` v89 only copies external microcode images when the initramfs lacks embedded microcode; the Felunyx initramfs embeds microcode through its configured `microcode` hook, so those files were never present in the final image. This was corrected by referencing only the kernel and initramfs, matching the locked `releng` v89 profile, and a fail-closed payload validator now rejects any ISO whose EFI/syslinux entries reference missing files. This artifact must not be used for the Virtual gate because its live entries are broken.

## Remote gate

**State: pending.**

Source tests and one development build are useful evidence, but the complete gate still requires reviewed proof for:

- exact build-environment and source locks;
- resolved `releng` delta and package contents;
- integration and frozen build behavior;
- safe cleanup and preserved failure evidence;
- checksums, manifests, source locks, logs, and provenance;
- two independent frozen builds and comparison evidence;
- R1 and R2 results, with an explicit R3 result or structured differences;
- absence of secrets, enabled SSH, production signing material, and unsafe workflow inputs.

No full Remote-gate pass is recorded here.

## Virtual gate

**State: pending.**

The hardened workflow must run against a matching rebuilt ISO and produce reviewed results for all required scenarios:

1. live UEFI Linux Zen;
2. live UEFI Linux LTS;
3. successful Calamares installation to a fresh GPT/Btrfs disk;
4. installed UEFI/GRUB Linux Zen plus verified one-shot LTS preparation;
5. installed UEFI/GRUB Linux LTS on the same disk;
6. controlled `FelunyxInjectedFailure` with actionable transported logs.

BIOS remains best-effort and is recorded separately. Missing, malformed, skipped, cancelled, blocked, or unrecorded required evidence is never a pass.

No scenario is currently recorded as `validated in VM` for the hardened source.

## Hardware queue

**State: not tested.**

Hardware validation remains explicitly separate:

- physical UEFI USB boot;
- firmware variation;
- real GPU and display behavior;
- wired and wireless network devices;
- physical storage installation and recovery;
- suspend, resume, power management, and battery behavior;
- peripherals and multi-monitor behavior.

No item is currently recorded as `validated in hardware`.

## Review boundary

- Keep PR #3 and PR #5 draft and unmerged.
- Complete the remaining Remote evidence and review it explicitly.
- Build a matching ISO from the hardening source before running the hardened Virtual workflow.
- Review every required scenario artifact before changing the Virtual gate state.
- Do not begin Phase 3 implementation from PR #6 or another branch until Mafu explicitly approves the Phase 2 review boundary.
