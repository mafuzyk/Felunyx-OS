# Phase 2 Source Ledger

**Research date:** 2026-08-04

This ledger records the external contracts used to design the Phase 2 ISO. It is evidence for decisions, not a frozen substitute for checking the exact versions selected during implementation.

Priority order:

1. current upstream source and manuals;
2. ArchWiki and Arch manual pages;
3. official project documentation;
4. archived source only to understand historical configuration contracts, with explicit caveats;
5. community material only as a lead, never as the sole authority for a critical decision.

## Sources

### S-001 — Archiso overview

- URL: https://wiki.archlinux.org/title/Archiso
- Authority: ArchWiki
- Supports: use of `archiso`; `releng` as the official monthly-ISO profile and customization starting point; profile structure; UEFI and BIOS paths; QEMU/OVMF testing; work-directory mount warning.
- Design effects: committed `releng` lineage, UEFI-required/Bios-best-effort policy, `run_archiso`/QEMU investigation, guarded work-tree cleanup.
- Caveat: Wiki guidance follows current Arch and must be paired with the exact locked `archiso` release.

### S-002 — `mkarchiso` manual

- URL: https://man.archlinux.org/man/mkarchiso.1.en
- Authority: Arch package manual
- Supports: `mkarchiso` input/output contract, pacman configuration, install directory and ISO label constraints, work/output directories, profile-directory invocation.
- Design effects: repository scripts wrap `mkarchiso`; identity fields are validated; profile path is explicit.
- Caveat: option availability is tied to the locked `archiso` version.

### S-003 — Arch Linux Archive

- URL: https://wiki.archlinux.org/title/Arch_Linux_Archive
- Authority: ArchWiki
- Supports: daily repository snapshots and exact historical package epochs; warning against mixing archived and current mirrors.
- Design effects: frozen build mode, source date lock, hard failure instead of fallback to current repositories.
- Caveat: very old packages may move to the historical archive and keyring history can complicate verification.

### S-004 — Arch reproducible builds

- URL: https://wiki.archlinux.org/title/Reproducible_builds
- Authority: ArchWiki / Arch reproducibility effort
- Supports: Arch is still working toward reproducibility for all packages; byte differences can originate in upstream packages and tooling; `repro` and `diffoscope`-style investigation.
- Design effects: R1/R2/R3 levels; Phase 2 requires inputs and functional payload, investigates byte differences instead of promising universal byte identity.
- Caveat: the page notes known keyring and test-environment issues.

### S-005 — `xorriso` manual

- URL: https://man.archlinux.org/man/xorriso.1
- Authority: upstream manual packaged by Arch
- Supports: ISO creation, fixed timestamp controls, `SOURCE_DATE_EPOCH`, reproducibility requirements, dependence on exact `xorriso` version and input metadata.
- Design effects: build epoch and tool versions recorded; R3 comparison; ISO metadata difference report.
- Caveat: different `xorriso` versions may legitimately produce different output.

### S-006 — GitHub-hosted runners

- URL: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- Authority: GitHub documentation
- Supports: standard public Linux runner is a fresh VM with 4 CPUs, 16 GB RAM, and 14 GB SSD; `ubuntu-slim` is an unprivileged container unsuitable for mounts, Docker-in-Docker, and low-level kernel operations.
- Design effects: standard `ubuntu-24.04` first executor, storage preflight, explicit prohibition on `ubuntu-slim` for image builds.
- Caveat: runner images and available labels evolve; workflow logs must record the actual runner image.

### S-007 — Secure use of GitHub Actions

- URL: https://docs.github.com/en/actions/reference/security/secure-use
- Authority: GitHub documentation
- Supports: full-length commit SHA is the immutable way to pin an action; action source should be audited.
- Design effects: SHA-pinned actions, minimum permissions, no untrusted privileged builds.
- Caveat: pinning prevents tag movement but does not replace source review.

### S-008 — Self-hosted runners

- URL: https://docs.github.com/en/actions/reference/runners/self-hosted-runners
- Authority: GitHub documentation
- Supports: replaceable runner machines and operator responsibility for resources and software.
- Design effects: executor-independent build contract; dedicated VM fallback.
- Caveat: a privileged self-hosted runner attached to a public repository must not execute untrusted fork code.

### S-009 — GNU GRUB 2.14 manual

- URL: https://www.gnu.org/software/grub/manual/grub/html_node/Simple-configuration.html
- Authority: GNU GRUB upstream manual
- Supports: `GRUB_TOP_LEVEL` selects a kernel image as top-level entry; title-based defaults are discouraged because titles can be unstable or translated; submenu behavior is configurable.
- Design effects: Zen default selected by kernel path or stable identifier; LTS remains explicit and testable.
- Caveat: generated Arch scripts and packaged GRUB version must be tested together.

### S-010 — Btrfs subvolume manual

- URL: https://man.archlinux.org/man/btrfs-subvolume.8.html
- Authority: Btrfs manual packaged by Arch
- Supports: subvolume behavior and distinction between per-mount generic options and filesystem-wide specific options.
- Design effects: conservative mount options; no unproven per-device tuning; explicit snapshot boundaries.
- Caveat: many Btrfs-specific options affect the entire filesystem even when written on one subvolume mount.

### S-011 — Calamares project home

- URL: https://calamares.io/
- Authority: Calamares project
- Supports: Calamares remains a distribution-agnostic installer framework and development has moved to Codeberg.
- Design effects: fetch exact current release from the current upstream home; do not follow the archived GitHub repository as a floating source.
- Caveat: website migration means some older documentation and links still refer to GitHub.

### S-012 — Calamares user guide

- URL: https://calamares.io/docs/users-guide/
- Authority: Calamares project documentation
- Supports: common installer module flow and modular/distribution-configured behavior.
- Design effects: minimal Phase 2 page sequence and separation of upstream package from Felunyx configuration.
- Caveat: the guide is user-oriented and older than current releases; exact module configuration must be verified against locked source.

### S-013 — Calamares partition guide

- URL: https://calamares.io/docs/partitions/
- Authority: Calamares project documentation
- Supports: automated and manual partition choices; GPT as the modern UEFI path; installer consequences.
- Design effects: UEFI/GPT required virtual install; manual path not claimed complete; destructive summary.
- Caveat: exact current KPMCore and module capabilities must be tested.

### S-014 — Calamares summary guide

- URL: https://calamares.io/docs/summary/
- Authority: Calamares project documentation
- Supports: summary before irreversible changes and final confirmation.
- Design effects: no preselected erase, complete technical review before formatting.
- Caveat: Felunyx must verify which details are surfaced by the exact configuration and add branding/modules when needed.

### S-015 — Calamares issue guidance

- URL: https://calamares.io/issues/
- Authority: Calamares project documentation
- Supports: diagnostic logs, Calamares and KPMCore versions, ISO/config context, firmware/partition-table details.
- Design effects: retained session/install logs and complete build/version context in V artifacts.
- Caveat: current issue tracker location may follow the project migration.

### S-016 — Archived Calamares `partition.conf`

- URL: https://github.com/calamares/calamares/blob/calamares/src/modules/partition/partition.conf
- Authority: archived upstream source example
- Supports historically documented keys for EFI size, partition defaults, GPT/hybrid layout, swap choices, LUKS generation, custom layouts, and initial choice `none`.
- Design effects: initial policy proposal and checklist for the exact current source review.
- Caveat: the repository is archived. No key is accepted in implementation until verified against the locked current Codeberg release.

### S-017 — Archived Calamares `mount.conf`

- URL: https://github.com/calamares/calamares/blob/calamares/src/modules/mount/mount.conf
- Authority: archived upstream source example
- Supports historically documented Btrfs subvolume list, swap subvolume, EFI `umask=0077`, and `compress=zstd:1` example.
- Design effects: proposed subvolume and mount policy.
- Caveat: exact schema and behavior must be verified against the locked current release before implementation.

### S-018 — Calamares tracking documentation

- URL: https://calamares.io/docs/tracking/
- Authority: Calamares project documentation
- Supports: tracking is optional and can transmit hardware data/IP only when enabled.
- Design effects: tracking module is excluded; Phase 2 has no telemetry.
- Caveat: absence of a module from the UI and execution sequence must be verified in the final config.

## Implementation-time refresh checklist

Before writing package or installer code, refresh:

- current `archiso` package and source release;
- exact `releng` profile content;
- current Arch Linux Archive snapshot availability;
- current stable Calamares release on Codeberg;
- exact Calamares `partition`, `mount`, bootloader, initramfs, unpack, and logging configuration schemas;
- current KPMCore requirements;
- current GRUB package behavior on Arch;
- current GitHub runner labels and resources;
- current OVMF/QEMU package names in the locked Arch snapshot.

A changed source may alter the implementation plan, but it must not silently alter the accepted product requirements.
