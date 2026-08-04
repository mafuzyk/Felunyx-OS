# Felunyx OS Phase 2 — Reproducible ISO Skeleton Design

**Date:** 2026-08-04

**Status:** Approved on 2026-08-04; implementation plan written

**Phase:** 2 — Reproducible ISO Skeleton

**Required completion gates:** Remote (R) and Virtual (V)

**Hardware gate:** Recorded for future validation; not required to close Phase 2

## 1. Executive summary

Phase 2 creates the smallest honest Felunyx system that can be built repeatedly, booted in a virtual machine, installed to a disposable virtual disk, and rebooted with both the default and fallback kernels.

It does not attempt to deliver the finished Felunyx desktop, package platform, recovery experience, hardware support matrix, or public release. Its job is to establish a trustworthy image pipeline and prove the base-system path on which later phases depend.

The selected design is deliberately close to upstream `archiso`, but it is not an untracked copy of the current `releng` profile. Felunyx commits its resolved profile, records the exact upstream baseline, and requires a reviewed difference report before adopting future `releng` changes.

The build environment is canonical and executor-independent. GitHub Actions is the first execution venue, not an architectural dependency. A pinned Arch build environment, ordinary repository scripts, and an executor-capability contract allow the same build to move to another VM or trusted runner if hosted CI cannot provide enough privilege, storage, or virtualization.

UEFI x86_64 is the required virtual boot path. BIOS remains included while it stays inexpensive and does not weaken UEFI. The installed Phase 2 system uses GRUB only. Limine receives an isolated research recipe and may be tested experimentally, but is not exposed as a supported Calamares choice until its installation and recovery path is proven.

## 2. Goal

Produce a reviewable, repeatable, internally installable Felunyx ISO with:

- a traceable `archiso` profile;
- Linux Zen as default kernel;
- Linux LTS as explicit fallback;
- UEFI boot validated in QEMU/OVMF;
- BIOS boot retained as best-effort compatibility;
- a minimal KDE Plasma Wayland live session;
- a minimal Felunyx-branded Calamares installation path;
- a Btrfs layout compatible with future system snapshots;
- GRUB installed on the target system;
- build locks, manifests, checksums, provenance, logs, and validation reports;
- two-build comparison for reproducible inputs and functional contents.

## 3. Non-goals

Phase 2 does not:

- ship a public alpha or stable release;
- claim broad hardware compatibility;
- finish Felunyx Central, Settings, Sets, rules, or recovery;
- finish the KDE reference experience;
- select permanent default applications;
- advertise Secure Boot;
- validate dual boot;
- validate encrypted installation end to end;
- support Limine as an installer choice;
- build production repository-signing infrastructure;
- promise byte-identical images when an upstream component is demonstrably nondeterministic;
- run privileged workflows on untrusted fork code;
- use absence of a failure as proof of hardware support.

## 4. Constraints

### 4.1 No local PC

The primary maintainer currently reviews from a phone. The design therefore maximizes remote and virtual evidence while preserving explicit hardware blockers.

### 4.2 Rolling base

Arch changes continuously. Felunyx needs both a current-integration build and a frozen investigation/reproduction build.

### 4.3 Privileged image construction

`mkarchiso` uses root privileges, mounts, loop devices, package installation into a root filesystem, and ISO-generation tooling. The build must run only where those capabilities are available and must fail before changing state when they are not.

### 4.4 Limited hosted-runner storage

The standard public Linux runner currently provides 14 GB of SSD. Work trees, package caches, root filesystem images, ISO output, and comparison builds can exceed this. The build must measure free space before execution, clean safely, and support a larger replacement executor.

### 4.5 Installer ownership

Calamares is a distribution integration framework. Felunyx owns its package recipe, exact version lock, configuration, modules enabled, logs, and target-system behavior. Upstream defaults are references, not a substitute for distribution testing.

## 5. Approved approaches

Three architectural choices were reviewed conversationally and approved before this document.

### 5.1 ISO structure

#### Approach A — Minimal unstructured copy

Copy `releng`, edit it directly, and add structure later.

- Fast first commit.
- High risk of hidden coupling and eventual demolition.

#### Approach B — Full product architecture immediately

Create profile composition, several desktop variants, package-generation layers, and release channels before the first ISO.

- Scales in theory.
- Introduces abstractions before evidence and violates YAGNI.

#### Approach C — Simple profile with prepared boundaries

Keep a committed, recognizable `archiso` profile while separating build environment, installer, manifests, branding, tools, and tests.

- Low initial complexity.
- Clear growth path.
- No premature multi-profile framework.

**Decision:** Approach C.

### 5.2 Firmware support

#### Approach A — UEFI only

Simplest validation, but needlessly drops inexpensive compatibility available in `releng`.

#### Approach B — UEFI and BIOS as equal release gates

Broad compatibility, but doubles critical paths and lets legacy support block modern reliability.

#### Approach C — UEFI required, BIOS best-effort

UEFI x86_64 is fully validated. BIOS remains while inherited support is cheap and non-disruptive.

**Decision:** Approach C.

### 5.3 Build execution

#### Approach A — Install everything in each workflow

Makes GitHub Actions the undocumented build system and increases drift.

#### Approach B — Fixed container tied to GitHub

Improves consistency but still couples the build contract to one provider.

#### Approach C — Canonical environment, replaceable executor

A pinned Arch environment and repository scripts define the build. GitHub Actions only supplies a machine.

**Decision:** Approach C.

## 6. Validation contract

Phase 2 requires both R and V.

### 6.1 Remote gate (R)

R passes when:

- source and environment locks are complete;
- schemas and configuration validate;
- explicit packages resolve against the selected repository snapshot;
- image contents and permissions validate;
- two frozen builds have equivalent package manifests and declared functional payloads;
- build artifacts include provenance and logs;
- workflows pass security checks;
- no secret or private signing key exists in the repository or ISO;
- the `releng` delta is machine-readable and reviewed.

### 6.2 Virtual gate (V)

V passes when:

- the ISO boots through UEFI with QEMU/OVMF;
- the live system reaches its declared target;
- Plasma Wayland or its display-manager/session evidence is observable;
- Linux Zen boots as default;
- Linux LTS can be deliberately selected and booted;
- Calamares installs to a disposable GPT virtual disk;
- the installed system reboots through GRUB;
- both installed kernels boot;
- the Btrfs subvolume and mount layout matches the specification;
- an injected installation failure retains actionable logs.

### 6.3 Hardware queue (H)

Phase 2 records but does not require:

- boot from physical USB media;
- real UEFI implementations;
- physical graphics and Wi-Fi;
- NVMe/SATA/USB target disks;
- real suspend, resume, input, audio, Bluetooth, and multi-monitor behavior.

No Phase 2 artifact is described as hardware-supported solely because it passed QEMU.

## 7. Reproducibility levels

### R1 — Reproducible inputs

The build records and can restore:

- Felunyx commit;
- `archiso` version and upstream baseline;
- Arch repository snapshot date;
- container image digest;
- package versions;
- build-script versions;
- configuration payload;
- `SOURCE_DATE_EPOCH`;
- ISO-generation tool versions.

### R2 — Reproducible functional contents

Two builds from the same inputs produce equivalent:

- package manifests;
- configured root filesystem payload, excluding explicitly documented volatile fields;
- boot configuration;
- kernel and initramfs inventory;
- Calamares configuration;
- enabled services;
- permissions and ownership;
- provenance metadata.

### R3 — Byte-reproducible ISO

Two images have the same SHA-256.

Phase 2 requires R1 and R2. R3 is attempted. If R3 fails, the build emits a structured difference report. A known upstream timestamp, ordering, filesystem-image, or tool-version difference may keep R3 open without blocking Phase 2 only when R1 and R2 pass and the difference cannot affect behavior.

## 8. Repository structure

The implementation plan may refine file names, but responsibility boundaries are fixed:

```text
build/
├── Containerfile
├── environment.lock
└── README.md

iso/
├── profile/
│   ├── airootfs/
│   ├── efiboot/
│   ├── grub/
│   ├── syslinux/
│   ├── packages.x86_64
│   └── profiledef.sh
├── upstream/
│   └── releng.lock
├── branding/
└── README.md

installer/
├── calamares/
├── branding/
└── README.md

packages/
├── bootstrap/
├── calamares/
├── felunyx-calamares-config/
├── felunyx-iso-hooks/
└── manifests/

tools/
├── felunyx-build
├── felunyx-validate
├── felunyx-run-vm
├── felunyx-compare-builds
└── sync-releng

tests/
├── iso/
├── boot/
├── installer/
└── fixtures/
```

No empty directories are committed merely to match this diagram. Each directory appears with its first owned deliverable.

## 9. `releng` lineage

### 9.1 Committed resolved profile

Felunyx commits the actual profile used by `mkarchiso` under `iso/profile/`.

The build never copies the host’s current `/usr/share/archiso/configs/releng` at runtime. That would make a source update silently change the ISO without a reviewable diff.

### 9.2 Baseline lock

`iso/upstream/releng.lock` records:

- `archiso` package version;
- package archive checksum;
- upstream source commit or release identifier;
- import date;
- paths imported;
- Felunyx commit that accepted the baseline.

### 9.3 Updating the baseline

`tools/sync-releng`:

1. fetches or extracts a selected `releng` version into a temporary directory;
2. verifies its checksum or source identity;
3. compares it to the recorded baseline and Felunyx profile;
4. emits a human-readable report and machine-readable change list;
5. never modifies the committed profile without an explicit apply step;
6. never auto-merges upstream changes.

This makes upstream drift visible while keeping the working profile understandable.

## 10. Build modes

### 10.1 Integration build

Uses current Arch repositories.

Purpose:

- detect rolling-release changes early;
- reveal removed packages, changed dependencies, and `archiso` incompatibilities;
- keep Felunyx aligned with current Arch.

Claims:

- current integration evidence only;
- no historical reproduction guarantee.

### 10.2 Frozen build

Uses one exact Arch Linux Archive repository date and locked build tools.

Purpose:

- reproduce a candidate;
- compare clean builds;
- investigate regressions;
- preserve Phase 2 evidence.

Frozen and current mirrors are never mixed. A package download failure must fail the build rather than fall through to a different repository epoch.

### 10.3 Build clock

`SOURCE_DATE_EPOCH` is set from a declared source, normally the accepted Felunyx commit timestamp or an explicitly recorded build epoch. The value is stored in provenance.

Tool versions remain locked because `SOURCE_DATE_EPOCH` alone cannot compensate for output changes between different `xorriso`, filesystem, compression, or `archiso` versions.

## 11. Canonical build environment

### 11.1 Environment lock

The build environment is an Arch OCI image identified by immutable digest plus a lock of installed build packages.

The lock includes at least:

- `archiso`;
- `pacman`;
- `archlinux-keyring`;
- `squashfs-tools` or selected rootfs image tools;
- `libisoburn`/`xorriso`;
- QEMU tooling used in V tests;
- OVMF firmware package;
- validation utilities;
- shell and schema linting tools.

### 11.2 Executor contract

Before building, the executor preflight reports:

- architecture;
- kernel;
- root/sudo availability;
- mount capability;
- loop-device availability;
- container runtime;
- free disk and inode count;
- available RAM and CPU;
- `/dev/kvm` availability;
- QEMU and OVMF availability;
- output and temporary-directory paths.

A missing required capability fails before package installation or mount creation.

### 11.3 First executor

The first executor is a standard `ubuntu-24.04` GitHub-hosted VM, not `ubuntu-slim`.

The workflow starts the pinned Arch environment with only the privileges and mounts needed by the build. If the hosted runner proves insufficient, only the executor layer changes.

### 11.4 Replacement executor

A dedicated VM or self-hosted runner may replace GitHub-hosted execution when storage, privilege, time, or virtualization requires it.

Because the repository is public, a self-hosted privileged runner must not execute fork pull-request code. Full builds run only from trusted branches, scheduled workflows, or manually approved dispatches.

## 12. Work-directory safety

`mkarchiso` can leave bind mounts after interruption. The build therefore treats work-directory deletion as a privileged recovery action.

Rules:

- create a unique work directory below the executor’s temporary root;
- never use the repository checkout as the work directory;
- record the path in the build log;
- install signal and exit traps;
- run `findmnt` against the work tree before cleanup;
- unmount only mounts whose source and target match the current build record;
- refuse recursive deletion while mounts remain;
- never run an unguarded `rm -rf` on a caller-supplied path;
- retain a cleanup report when interrupted;
- allow an operator to preserve the failed tree for diagnosis.

## 13. Build artifacts

Every successful frozen build produces:

```text
Felunyx-OS-phase2-<commit>-x86_64.iso
SHA256SUMS
packages.txt
build-info.json
source-lock.json
validation-report.json
build.log
```

Virtual tests add:

```text
uefi-boot.log
lts-boot.log
installer.log
installed-zen-boot.log
installed-lts-boot.log
btrfs-layout.json
failure-injection.log
```

A reproducibility comparison may add:

```text
comparison-report.json
iso-metadata.diff
filesystem-payload.diff
```

The build does not upload package caches, secrets, mutable work directories, or duplicated root filesystem images unless explicitly needed to diagnose a failed trusted run.

## 14. ISO identity

Phase 2 uses an internal artifact identity, not a public version promise.

Required identity fields:

- formal name: `Felunyx OS`;
- short ID: `felunyx`;
- artifact channel: `phase2` or `development`;
- architecture: `x86_64`;
- volume label and install directory within `mkarchiso` limits;
- `/etc/os-release` identifying Felunyx and its Arch relationship;
- build commit, source snapshot, and build epoch available in `/usr/lib/felunyx/build-info.json` or an equivalent immutable path.

The live hostname is `felunyx-live`.

## 15. Live-media boot

### 15.1 Separation from installed boot

Live-media boot follows the selected `archiso` profile mechanisms. Installed-system boot follows the installer specification.

The project does not force the installed GRUB design into the ISO’s boot path merely for conceptual uniformity.

### 15.2 UEFI

UEFI x86_64 is required.

The profile contains explicit boot entries for:

- Felunyx OS — Linux Zen;
- Felunyx OS — Linux LTS;
- firmware setup or relevant upstream utility when inherited and validated.

Zen is the default. LTS is visible and deliberately selectable.

### 15.3 BIOS

BIOS support remains inherited from `releng` through Syslinux/ISOLINUX while:

- the required packages remain available;
- the configuration does not complicate UEFI;
- the image-size and maintenance cost stay reasonable;
- no BIOS-specific workaround weakens the required path.

BIOS smoke tests run when cheap. A BIOS-only failure is recorded but does not block Phase 2.

## 16. Kernels, firmware, and microcode

The live and installed system include:

- `linux-zen`;
- `linux-lts`;
- `linux-firmware`;
- AMD and Intel microcode packages;
- initramfs for both kernels.

Kernel entries and initramfs are validated as pairs. Presence of package names alone is insufficient.

## 17. Installed-system boot

Phase 2 supports GRUB as the installed bootloader.

Zen is selected through a stable kernel path or equivalent generated configuration, not a numeric menu index or translated title. Linux LTS remains an explicit fallback entry.

Limine is not offered in Calamares during Phase 2. Research may document package installation and a VM proof separately, but it cannot alter required exit criteria.

## 18. Calamares ownership

Felunyx packages Calamares and its configuration separately.

- the framework package uses an exact release, source hash, signature, and build options;
- the configuration package owns settings, branding, module files, and Felunyx integration;
- the profile consumes packages rather than copying an uncontrolled runtime tree;
- archived GitHub examples are accepted only after their keys are confirmed against the locked release source.

The initial sequence is welcome, locale, keyboard, partition, users, summary, install, finished. Tracking is absent.

## 19. Storage layout

Automatic installation uses GPT and Btrfs.

- ESP: FAT32, `/boot/efi`, 1 GiB recommended, 512 MiB minimum;
- `@` → `/`;
- `@home` → `/home`;
- `@snapshots` → `/.snapshots`;
- `@cache` → `/var/cache`;
- `@log` → `/var/log`;
- optional `@swap` for a Btrfs swapfile.

System rollback can later restore `@` while preserving `@home`, `@log`, cache policy, and snapshot storage.

## 20. Installer safety

Erase is not preselected. The summary names disks, partitions, formats, mounts, bootloader, kernels, and destructive effects.

Phase 2 validates unencrypted automatic installation end to end. Encryption remains visible only if the locked boot/initramfs path is verified; otherwise it is deferred rather than falsely advertised.

## 21. Minimal Plasma live session

The live session includes enough Plasma Wayland functionality to launch Calamares, connect network, inspect disks/logs, use terminal and file manager, and prove Felunyx identity.

It does not freeze the Phase 4 launcher, panel, animation, icon, sound, or application-selection design.

The live user autologs in and has passwordless sudo only in live media. SSH is disabled.

## 22. Local package repository

Phase 2 builds Felunyx packages before the ISO, creates an unsigned development repository local to the build, and records explicit bootstrap trust boundaries.

No production signing key is generated or stored. Production repository trust belongs to Phase 7.

## 23. Static validation

Validation covers:

- source locks and checksums;
- package resolution;
- profile syntax and identity;
- boot files and kernel/initramfs pairs;
- enabled units;
- permissions;
- Calamares sequence and storage configuration;
- absence of SSH, telemetry, private keys, and secrets;
- artifact checksums and metadata;
- frozen/current mirror separation;
- safe cleanup behavior.

## 24. Virtual validation

QEMU/OVMF tests collect semantic evidence through serial, guest state, logs, and stable interfaces.

No test relies on image-coordinate clicking. Installer automation uses a supported unattended, module, test, or accessibility interface. If none exists, the limitation is documented as a V blocker rather than bypassed dishonestly.

## 25. Workflow security

Untrusted pull requests run only static, unprivileged checks. Trusted branches, schedules, or approved manual dispatches run privileged builds and VM tests.

Actions are pinned to full commit SHAs; permissions are minimal; credentials are not persisted; workdirs and caches are not uploaded.

## 26. Error handling

- capability failure occurs before privileged state changes;
- frozen package absence aborts instead of mixing epochs;
- interrupted build retains logs and guarded cleanup state;
- mount cleanup refuses unsafe deletion;
- build artifacts publish atomically;
- canceled or skipped tests report `not-run`, never pass;
- installer failure retains exact stage and logs;
- no success claim is made without the matching gate evidence.

## 27. Proposed Phase 2 decisions

| ID | Decision |
|---|---|
| P2-001 | Commit the resolved releng-derived profile and track its upstream baseline. |
| P2-002 | Lock archiso 89-1 for the first implementation baseline. |
| P2-003 | Use a canonical pinned Arch environment with a replaceable executor. |
| P2-004 | Separate current integration and frozen Archive builds. |
| P2-005 | Require R1 and R2; measure and report R3. |
| P2-006 | Require UEFI x86_64; keep BIOS best-effort. |
| P2-007 | Use Zen default and LTS fallback in live and installed systems. |
| P2-008 | Support installed GRUB only in Phase 2. |
| P2-009 | Keep Limine isolated as research. |
| P2-010 | Package Calamares 3.3.14 separately from Felunyx config. |
| P2-011 | Use GPT, FAT32 ESP at /boot/efi, and Btrfs automatic installation. |
| P2-012 | Use @, @home, @snapshots, @cache, @log, and conditional @swap. |
| P2-013 | Start with compress=zstd:1 and conservative mount options. |
| P2-014 | Use minimal Plasma Wayland only as a validation surface. |
| P2-015 | Keep passwordless sudo and autologin live-only. |
| P2-016 | Disable SSH and exclude telemetry. |
| P2-017 | Keep workdirs unique and outside checkout. |
| P2-018 | Refuse cleanup while mounts remain. |
| P2-019 | Publish manifest, provenance, checksums, logs, and validation reports. |
| P2-020 | Run privileged builds only on trusted inputs. |
| P2-021 | Pin external actions by full SHA. |
| P2-022 | Run capability and free-space preflight before build. |
| P2-023 | Require QEMU/OVMF, both kernels, installation, GRUB reboot, and Btrfs inspection for V. |
| P2-024 | Record BIOS separately without making it a gate. |
| P2-025 | Use semantic installer automation, never coordinate clicking. |

## 28. Explicitly deferred Phase 2 details

The exact OCI digest, frozen Archive date, current releng file hashes, package versions beyond fixed top-level locks, exact supported Calamares automation interface, and whether R3 passes are resolved by the implementation tasks and recorded as evidence. They are not product ambiguities.

## 29. Acceptance criteria

The design is ready for implementation because:

- approved approaches are explicit;
- source hierarchy and locks are defined;
- required and best-effort boot paths are separated;
- package/installer ownership is explicit;
- storage names and mount policy are fixed;
- R/V/H claims are separated;
- failures and cleanup are designed;
- security boundaries are explicit;
- every deferred implementation detail has an evidence trigger;
- the implementation plan exists at `docs/superpowers/plans/2026-08-04-phase-2-reproducible-iso.md`.
