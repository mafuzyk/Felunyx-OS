# Phase 2 Source Ledger

**Research date:** 2026-08-04

This ledger records the external contracts used to design and plan the Phase 2 ISO. It is evidence for decisions, not a substitute for checking the exact locked versions during implementation.

Priority order:

1. current upstream source and manuals;
2. ArchWiki and Arch manual pages;
3. official project documentation;
4. archived source only to understand historical configuration contracts, with explicit caveats;
5. community material only as a lead, never as the sole authority for a critical decision.

## Locked implementation facts

- `archiso`: `89-1`, published by Arch on 2026-07-27.
- Calamares: `3.3.14`, source SHA-256 `5547f80db067dea923ae693ba6bb88eb2b2eeac1da3ebec42fce453e31c290c0`.
- Calamares signing fingerprint: `6D98B995A1CA6CE4BB906518C7AA337DFA13881E`.
- First hosted executor label: `ubuntu-24.04`.
- Current public-runner envelope: 4 CPUs, 16 GB RAM, 14 GB SSD.

## Sources

### S-001 — Archiso overview

- URL: https://wiki.archlinux.org/title/Archiso
- Authority: ArchWiki
- Supports: `releng` as the official monthly-ISO profile and customization starting point; UEFI/BIOS paths; QEMU/OVMF testing; interrupted-workdir mount warning.
- Design effects: committed `releng` lineage, UEFI-required/BIOS-best-effort policy, guarded work-tree cleanup.

### S-002 — Archiso package 89-1

- URL: https://archlinux.org/packages/extra/any/archiso/
- Authority: Arch package database
- Supports: current exact version, package signature metadata, optional `edk2-ovmf`, `qemu-desktop`, and GRUB integration.
- Design effects: first baseline lock and virtual-test dependencies.

### S-003 — `mkarchiso` manual

- URL: https://man.archlinux.org/man/mkarchiso.1.en
- Authority: Arch package manual
- Supports: input/output, pacman configuration, label/install-directory constraints, work/output directories, and profile invocation.

### S-004 — Arch Linux Archive

- URL: https://wiki.archlinux.org/title/Arch_Linux_Archive
- Authority: ArchWiki
- Supports: daily repository snapshots and warning against mixing archived and current mirrors.
- Design effects: frozen build mode and hard failure rather than epoch fallback.

### S-005 — Arch reproducible builds

- URL: https://wiki.archlinux.org/title/Reproducible_builds
- Authority: Arch reproducibility effort
- Supports: byte differences may originate upstream; investigation tools and limitations.
- Design effects: R1/R2/R3 levels and structured difference reports.

### S-006 — `xorriso` manual

- URL: https://man.archlinux.org/man/xorriso.1
- Authority: upstream manual packaged by Arch
- Supports: ISO creation, fixed timestamp controls, `SOURCE_DATE_EPOCH`, and exact-tool-version relevance.

### S-007 — GitHub-hosted runners

- URL: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- Authority: GitHub documentation
- Supports: public `ubuntu-24.04` is a fresh VM with 4 CPUs, 16 GB RAM and 14 GB SSD; `ubuntu-slim` is an unprivileged container unsuitable for mounts and low-level kernel work.
- Design effects: standard VM executor, free-space preflight, prohibition on slim builds.

### S-008 — Secure GitHub Actions use

- URL: https://docs.github.com/en/actions/reference/security/secure-use
- Authority: GitHub documentation
- Supports: full-length commit SHA is the immutable way to pin actions.
- Design effects: SHA-pinned actions and source review.

### S-009 — Self-hosted runners

- URL: https://docs.github.com/en/actions/reference/runners/self-hosted-runners
- Authority: GitHub documentation
- Supports: replaceable operator-owned machines.
- Design effects: executor independence and prohibition on privileged untrusted fork runs.

### S-010 — GNU GRUB manual

- URL: https://www.gnu.org/software/grub/manual/grub/html_node/Simple-configuration.html
- Authority: GNU GRUB upstream
- Supports: `GRUB_TOP_LEVEL` and instability of title-based defaults.
- Design effects: stable Zen default and explicit LTS fallback.

### S-011 — Btrfs subvolume manual

- URL: https://man.archlinux.org/man/btrfs-subvolume.8.html
- Authority: Btrfs manual packaged by Arch
- Supports: subvolume behavior and filesystem-wide impact of several Btrfs-specific mount options.
- Design effects: conservative `compress=zstd:1`, no speculative hardware tuning.

### S-012 — Calamares project home/about

- URLs: https://calamares.io/ and https://calamares.io/about/
- Authority: Calamares project
- Supports: development moved to Codeberg, Qt 6/C++17/Python/YAML architecture, current release signing fingerprint.

### S-013 — Calamares 3.3.14 release

- URLs: https://calamares.io/news/ and https://github.com/calamares/calamares/releases/tag/v3.3.14
- Authority: Calamares release publication and archived release mirror
- Supports: exact release, source SHA-256, signing fingerprint, and release notes.
- Caveat: GitHub repository is archived; release artifacts remain useful for reproducible source identity while current development is on Codeberg.

### S-014 — Calamares user, partition, summary, issue and tracking guides

- URLs: https://calamares.io/docs/users-guide/, https://calamares.io/docs/partitions/, https://calamares.io/docs/summary/, https://calamares.io/issues/, https://calamares.io/docs/tracking/
- Authority: Calamares documentation
- Supports: modular installer flow, pre-destructive summary, diagnostic requirements, optional tracking.
- Design effects: minimal sequence, no preselected erase, retained logs, no tracking module.

### S-015 — Archived Calamares `partition.conf`

- URL: https://github.com/calamares/calamares/blob/calamares/src/modules/partition/partition.conf
- Authority: archived upstream example
- Supports historical keys for EFI sizing, GPT, filesystem choice, swap, LUKS and initial selection.
- Caveat: every used key must be verified against the locked 3.3.14 source.

### S-016 — Archived Calamares `mount.conf`

- URL: https://github.com/calamares/calamares/blob/calamares/src/modules/mount/mount.conf
- Authority: archived upstream example
- Supports Btrfs subvolume list, swap subvolume, EFI `umask=0077`, and `compress=zstd:1` example.
- Caveat: schema and behavior must be verified against locked source.

## Implementation-time refresh checklist

Before publishing the implementation PR, verify and record:

- immutable Arch OCI base-image digest;
- exact `releng` 89-1 file inventory and hashes;
- one viable frozen Archive date containing the complete package set;
- exact Calamares 3.3.14 build dependencies on the selected Archive date;
- exact module schemas from the locked source;
- current GRUB generation behavior on the selected package epoch;
- current runner image identity and actual free space;
- exact OVMF/QEMU paths and KVM availability.

A changed source may alter an implementation detail, but it must not silently alter the accepted product requirements.
