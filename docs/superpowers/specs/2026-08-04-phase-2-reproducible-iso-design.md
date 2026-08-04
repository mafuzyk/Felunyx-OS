# Felunyx OS Phase 2 — Reproducible ISO Skeleton Design

**Date:** 2026-08-04

**Status:** Written and self-reviewed; awaiting user review

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
- corresponding headers only when an actual Phase 2 package requires them;
- `linux-firmware` and required firmware split packages according to the locked Arch snapshot;
- Intel microcode;
- AMD microcode.

Tests verify that each kernel has:

- a kernel image;
- a generated initramfs;
- a boot entry;
- a successful virtual boot.

Package ordering is never used to infer the default kernel.

## 17. Installed bootloader

### 17.1 GRUB is the Phase 2 supported path

The target system installs GRUB to a GPT/UEFI layout and generates a visible menu.

`GRUB_TOP_LEVEL=/boot/vmlinuz-linux-zen` or an equivalently robust, tested mechanism makes Zen the top-level candidate. Felunyx does not select a default through translated menu text or unstable numeric position.

Linux LTS remains visible as a fallback and is booted in V tests.

### 17.2 Limine isolation

Limine remains an accepted future installer alternative, but Phase 2 does not expose it in Calamares.

Phase 2 may include:

- a package recipe;
- a documented target layout;
- static configuration validation;
- an optional standalone VM experiment.

Limine becomes an installer choice only after installation, kernel-update, fallback, recovery, and uninstall/migration behavior are specified and tested.

## 18. Bootstrap Felunyx repository

Calamares and Felunyx integration packages need a repository visible to `mkarchiso`.

The Phase 2 bootstrap repository contains only what is required to build and install the skeleton, such as:

- `felunyx-release`;
- `felunyx-keyring` development metadata, without a production private key;
- `felunyx-mirrorlist` for the build context;
- `calamares`;
- `felunyx-calamares-config`;
- `felunyx-iso-hooks`.

### 18.1 Trust model

No private signing key is committed, embedded, uploaded as an ordinary artifact, or exposed to pull requests.

Phase 2 may use an explicitly isolated development repository policy during trusted builds. That exception is:

- scoped only to the named bootstrap repository;
- visible in build configuration;
- forbidden in production claims;
- recorded in validation output;
- replaced by signed production repository infrastructure in Phase 7.

Package files still receive checksums and provenance. An ephemeral build key is not treated as durable user trust and is not used to pretend production signing exists.

## 19. Calamares ownership

### 19.1 Source

Felunyx builds Calamares from an exact stable upstream release source obtained from the project’s current home, with:

- tag or release identifier;
- source commit when available;
- source archive checksum;
- signature verification when the release provides one;
- build dependencies locked by the repository snapshot.

A floating branch, an archived GitHub snapshot, or an unreviewed prebuilt AUR package is not a valid source lock.

### 19.2 Separation

- `packages/calamares/` owns the upstream package recipe and minimal necessary patches.
- `packages/felunyx-calamares-config/` owns Felunyx branding, module sequence, partition policy, and installation behavior.
- patches require reason, tests, and removal/upstream plan.

### 19.3 Minimal flow

The Phase 2 installer presents only the modules necessary to prove the installation:

1. welcome and requirements;
2. locale/timezone;
3. keyboard;
4. partition choice;
5. user creation;
6. technical summary;
7. installation;
8. completion and reboot.

The execution sequence includes:

- mount preparation;
- root filesystem deployment;
- target configuration;
- locale and user creation;
- initramfs generation;
- GRUB installation and menu generation;
- service enablement;
- live-only package cleanup;
- final validation.

### 19.4 Destructive choice

The initial partitioning choice is `none`. “Erase disk” is never preselected.

The summary and final confirmation identify:

- target disk;
- partition table changes;
- partitions formatted;
- Btrfs layout;
- EFI partition;
- swap choice;
- bootloader;
- kernels;
- user and locale.

### 19.5 Logging

Calamares runs with enough diagnostic logging for Phase 2 evidence. Session and installation logs are copied to a known live location and uploaded from failed trusted VM runs.

A failed install must identify the failing module and preserve the target disk image long enough for automated inspection when storage permits.

## 20. Phase 2 storage design

### 20.1 Automatic-install scope

The required V installation path is:

- x86_64 UEFI;
- GPT;
- one EFI System Partition;
- one Btrfs system partition;
- optional Btrfs swapfile according to the selected Calamares choice;
- GRUB;
- no required encryption.

Manual partitioning may be visible for developer use but is not declared complete or supported by Phase 2. Dual boot and encrypted-install validation belong to Phase 5.

### 20.2 EFI System Partition

Recommended size: **1 GiB**.

Minimum accepted by the Felunyx automatic layout: **512 MiB**.

Mount point: `/boot/efi`.

Rationale:

- comfortable margin for bootloader files, multiple kernels, future Secure Boot artifacts, firmware quirks, and recovery work;
- avoids optimizing the foundation around the smallest currently possible GRUB footprint.

### 20.3 Btrfs subvolumes

The automatic layout creates:

| Subvolume | Mount point | Purpose |
|---|---|---|
| `@` | `/` | system state |
| `@home` | `/home` | user data, preserved by default during system restore |
| `@snapshots` | `/.snapshots` | snapshot namespace |
| `@cache` | `/var/cache` | disposable package/application cache |
| `@log` | `/var/log` | logs that should survive system rollback without rewinding |
| `@swap` | swapfile subvolume | swapfile isolation when selected |

This resolves the Phase 1 deferred naming decision once the Phase 2 specification is approved.

### 20.4 Mount options

Phase 2 uses conservative options:

- Btrfs: `defaults,compress=zstd:1`;
- EFI: `defaults,umask=0077`;
- Btrfs swap subvolume: `defaults,noatime` as required by the installer’s swapfile handling.

Phase 2 does not force:

- `autodefrag`;
- explicit `ssd`;
- `discard=async`;
- per-device performance tuning.

Those options affect the whole Btrfs filesystem or require hardware and workload evidence. Storage tuning belongs to the hardware-readiness phase.

## 21. Minimal KDE live profile

The Phase 2 desktop is a validation surface, not the final Felunyx reference experience.

It includes only enough to:

- start a graphical live session;
- launch Calamares;
- inspect logs and disks;
- access a terminal and file manager;
- connect to a network where virtual tests require it;
- demonstrate Felunyx identity without claiming final design.

### 21.1 Session

- SDDM starts the live session.
- The live user is automatically logged into Plasma Wayland.
- XWayland remains available for compatibility.
- Passwordless administrative access exists only in the live environment.
- The installed user follows normal password and privilege policy.
- SSH is disabled by Felunyx even if the upstream `releng` profile enables it.

### 21.2 Basic stack

The package manifest includes the minimum supported set for:

- Plasma Wayland;
- SDDM;
- NetworkManager;
- PipeWire and WirePlumber;
- relevant XDG portals;
- a terminal;
- a file manager;
- a browser only if needed for a useful internal image and storage permits;
- Calamares;
- disk and log diagnostics.

Exact end-user defaults remain deferred to Phase 4.

### 21.3 Branding

Phase 2 branding is intentionally narrow:

- boot labels;
- `/etc/os-release`;
- hostname;
- one wallpaper or solid branded background;
- installer name and basic marks;
- artifact metadata.

It does not freeze final icons, panel, launcher, window decoration, animation, sound, or design tokens.

## 22. Package manifests

One authoritative explicit package set is organized by responsibility, then rendered into the profile format.

Categories:

- base;
- boot and firmware;
- live system;
- Plasma session;
- installer;
- diagnostics;
- Felunyx bootstrap packages.

Validation rejects:

- duplicate explicit entries;
- unresolved packages;
- accidental AUR dependencies in the base profile;
- packages present only through an undocumented transitive dependency when Felunyx relies on them directly;
- live-only services leaking into the installed system;
- kernel without matching initramfs tooling.

The final `packages.txt` artifact records all installed packages, including dependencies.

## 23. Remote tests

R includes at least:

### 23.1 Documentation and schema

- shell syntax and linting;
- YAML/JSON/TOML validation;
- GitHub Actions linting;
- Calamares configuration schema or loader validation where available;
- package recipe parsing;
- relative documentation links;
- no incomplete requirement markers.

### 23.2 Package and source

- all explicit packages resolve in the chosen snapshot;
- bootstrap package checksums match;
- source archives match locks;
- no mixed current/archive repositories;
- no private keys or tokens;
- no package silently changes source identity.

### 23.3 Profile contents

- expected `/etc/os-release`;
- build provenance file;
- Zen and LTS images and initramfs;
- UEFI entries;
- BIOS files when enabled;
- SDDM and NetworkManager enablement;
- SSH disabled;
- Calamares configuration and launcher;
- correct permissions for shadow, sudoers, hooks, scripts, and keys;
- live-only cleanup metadata.

### 23.4 Build safety

- invalid work path rejected;
- mount-containing work path not deleted;
- interrupted cleanup fixture retains a report;
- insufficient disk and missing loop/mount capability fail preflight;
- executor output contains no secrets.

### 23.5 Reproducibility

Two clean frozen builds are compared for:

- source lock;
- package manifest;
- relevant rootfs tree metadata;
- boot configuration;
- installer configuration;
- ISO metadata;
- SHA-256.

When SHA-256 differs, comparison output isolates the difference rather than printing only “not reproducible.”

## 24. Virtual tests

### 24.1 Execution mode

QEMU uses KVM only when `/dev/kvm` is present and usable. Otherwise it uses TCG and records the slower mode.

The project never assumes nested virtualization is available merely because the host is a virtual machine.

### 24.2 UEFI boot

- OVMF firmware;
- serial console and graphical output retained;
- boot timeout;
- marker emitted when the target system state is reached;
- panic and emergency-shell detection;
- boot log uploaded.

### 24.3 Live Zen and LTS

Separate tests boot the default Zen entry and deliberately select the LTS entry. The guest reports `uname -r`, package identity, and build provenance.

### 24.4 Graphical session

The guest proves at least:

- display manager active;
- live user session active;
- Wayland session type;
- Plasma process present;
- Calamares executable and configuration readable.

A screenshot may be stored as supplemental evidence, but process and journal evidence remain primary.

### 24.5 Installation

A disposable QCOW2 disk is prepared as GPT/UEFI.

Installation automation uses the least brittle supported route available after Calamares packaging is fixed:

- an upstream-supported unattended/test mechanism;
- controlled UI automation with stable accessibility identifiers;
- or direct execution of the exact Calamares module sequence in a test harness.

The implementation plan must choose one only after inspecting the locked Calamares release. A fragile coordinate-based click script is not acceptable.

### 24.6 Installed boot

After installation:

1. remove the ISO;
2. boot GRUB;
3. verify Zen is default;
4. verify the expected Btrfs root and mount set;
5. reboot and select LTS;
6. verify LTS kernel identity;
7. retain both boot logs.

### 24.7 Failure injection

At least one controlled installation failure is introduced after logging begins. The test verifies:

- non-zero result;
- failing module identified;
- log preserved;
- no false success screen;
- target disk remains inspectable.

### 24.8 BIOS smoke

When the inherited path remains available, a short SeaBIOS/Syslinux smoke test verifies that the live ISO reaches an early boot marker. Failure is reported separately from the UEFI gate.

## 25. Workflow and supply-chain security

### 25.1 Pull requests

Untrusted pull requests run only non-privileged static R checks.

They do not receive:

- repository secrets;
- signing material;
- privileged containers;
- self-hosted runners;
- package publication permission;
- release write permission.

### 25.2 Trusted full builds

Privileged builds run only on:

- trusted branch pushes;
- manually approved dispatches;
- scheduled integration checks;
- explicit release-candidate tags in later phases.

### 25.3 Action dependencies

Third-party and GitHub Actions are pinned to full commit SHAs. Their source and necessity are reviewed. Workflow permissions are set explicitly to the minimum required.

### 25.4 Artifact policy

Artifacts have finite retention. Logs are scrubbed for tokens and credentials. Production secrets are absent from Phase 2.

## 26. Error handling

### 26.1 Package download failure

- fail without mixing repository epochs;
- preserve package and mirror context;
- retain partial cache only when verified and safe;
- identify the missing package and repository.

### 26.2 Source checksum failure

- stop before build;
- identify expected and actual digest;
- never update the lock automatically.

### 26.3 Insufficient storage

- fail preflight when obviously insufficient;
- report required, available, and largest existing paths;
- clean only registered temporary state;
- do not delete diagnostic artifacts needed to understand the failure.

### 26.4 Interrupted `mkarchiso`

- enumerate remaining mounts;
- attempt bounded cleanup;
- refuse unsafe deletion;
- produce a recovery command list and cleanup report.

### 26.5 QEMU timeout

- terminate guest cleanly, then force if necessary;
- preserve serial and QEMU logs;
- report last reached marker;
- distinguish infrastructure timeout from guest boot failure.

### 26.6 Installer failure

- preserve Calamares log;
- preserve module sequence and target layout;
- inspect the disposable target disk;
- never label a partially installed disk successful.

### 26.7 Reproducibility mismatch

- identify differing layers;
- compare package manifests first;
- compare source locks;
- compare rootfs and boot payload;
- inspect ISO metadata and timestamps;
- classify as functional mismatch, metadata-only mismatch, or unknown;
- unknown mismatch blocks R2.

## 27. Proposed Phase 2 decisions

These become canonical only after user review of this specification.

| ID | Proposed decision |
|---|---|
| P2-001 | Phase 2 requires R and V; H is a recorded future queue. |
| P2-002 | The ISO is based on a committed resolved `releng` profile with an upstream baseline lock and reviewed sync report. |
| P2-003 | The build uses a pinned Arch environment with a replaceable executor. |
| P2-004 | Standard `ubuntu-24.04` is the first hosted executor; `ubuntu-slim` is forbidden for image builds. |
| P2-005 | Integration and frozen builds are distinct and never mix repository epochs. |
| P2-006 | Phase 2 requires reproducible inputs and functional contents; byte identity is pursued and differences are classified. |
| P2-007 | UEFI x86_64 is required; BIOS remains best-effort while inexpensive and non-disruptive. |
| P2-008 | Live-media and installed-system boot architectures remain separate. |
| P2-009 | Linux Zen is default and Linux LTS is an explicit tested fallback. |
| P2-010 | GRUB is the only supported installed bootloader in Phase 2. |
| P2-011 | Limine remains isolated research until installation and recovery behavior is proven. |
| P2-012 | Calamares is built and pinned by Felunyx from current upstream release sources. |
| P2-013 | Calamares code packaging and Felunyx configuration are separate packages. |
| P2-014 | “Erase disk” is never preselected. |
| P2-015 | Required automatic installation is UEFI/GPT/Btrfs/GRUB without mandatory encryption. |
| P2-016 | The ESP is 1 GiB recommended and 512 MiB minimum at `/boot/efi`. |
| P2-017 | Btrfs subvolumes are `@`, `@home`, `@snapshots`, `@cache`, `@log`, and `@swap`. |
| P2-018 | Btrfs defaults to `compress=zstd:1`; hardware-specific tuning is deferred. |
| P2-019 | The Phase 2 KDE profile is a minimal validation surface, not the finished desktop experience. |
| P2-020 | SSH is disabled in the Felunyx live image. |
| P2-021 | No production signing key exists in Phase 2; bootstrap trust exceptions are explicit, isolated, and non-production. |
| P2-022 | Privileged builds never run on untrusted fork code. |
| P2-023 | Workflow actions are pinned to full commit SHAs. |
| P2-024 | Work-directory cleanup refuses deletion while mounts remain. |
| P2-025 | Calamares installation automation must use a supported/testable interface, not coordinate-based clicking. |

## 28. Explicitly deferred Phase 2 details

The following are not unspecified; they have evidence-based triggers.

### Exact `archiso` version and baseline commit

Chosen when implementation begins, then locked before the first profile commit. Trigger: current package and upstream release inspection.

### Exact Calamares release tag

Chosen from the current stable upstream release available at implementation planning, then locked by tag/commit/checksum. Trigger: direct inspection of the project’s current Codeberg release artifacts.

### Root filesystem image type and compression parameters

Use the current `releng` mechanism initially. Change only after measuring build size, memory, and boot time on the available executor. Trigger: first controlled build comparison.

### Browser in the live image

Included only if storage and utility justify it. The installer, terminal, file manager, diagnostics, and network remain higher priority. Trigger: initial image-size budget.

### Installation automation mechanism

Selected after the exact Calamares version is locked and its supported test/unattended interfaces are inspected. Trigger: package-source review before writing V tests.

### Dedicated runner

Introduced only if hosted-runner preflight or builds repeatedly fail because of storage, privileges, runtime, or virtualization. Trigger: retained executor reports.

## 29. Acceptance criteria for the written design

The design is ready for user review when:

- all approved C choices are represented;
- architecture, data flow, errors, and tests are explicit;
- every deferred item has a trigger;
- no implementation files are created before approval;
- source claims are traceable through the Phase 2 source ledger;
- R/V/H claims remain scoped;
- the specification has no placeholder requirements or contradictions.

## 30. Implementation boundary

After this specification is approved:

1. proposed Phase 2 decisions are added to the canonical decision register;
2. the Superpowers `writing-plans` skill produces a task-by-task implementation plan;
3. implementation begins on a separate branch or worktree according to that plan;
4. production code, ISO profiles, workflows, and package recipes are not created before those gates.
