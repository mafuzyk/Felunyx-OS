# Phase 2 Reproducible ISO Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a traceable Felunyx OS Phase 2 ISO that passes the Remote gate, then boots and installs in a disposable UEFI virtual machine for the Virtual gate.

**Architecture:** Felunyx commits a resolved `archiso` profile derived from a locked `releng` baseline and builds it through repository-owned scripts inside a pinned Arch environment. The live image contains Linux Zen, Linux LTS, a minimal Plasma Wayland session, Felunyx-owned Calamares packaging and configuration, while separate validators and QEMU harnesses produce structured evidence instead of relying on manual impressions.

**Tech Stack:** Arch Linux, archiso 89-1, Bash 5, Python 3.14 standard library, PKGBUILD/makepkg, Calamares 3.3.14, Qt 6/KDE Plasma, GRUB, Btrfs, QEMU, OVMF, GitHub Actions.

## Global Constraints

- UEFI x86_64 is required; BIOS is best-effort and never weakens UEFI.
- Linux Zen is default and Linux LTS is an explicit live and installed fallback.
- GRUB is the only supported installed bootloader in Phase 2; Limine remains isolated research.
- The `mkarchiso` profile is committed and never copied from the host at build time.
- The first baseline locks `archiso` to `89-1`.
- Calamares is locked to `3.3.14`, source SHA-256 `5547f80db067dea923ae693ba6bb88eb2b2eeac1da3ebec42fce453e31c290c0`, signing fingerprint `6D98B995A1CA6CE4BB906518C7AA337DFA13881E`.
- Current and frozen repositories are separate; frozen mode never falls through to current mirrors.
- Phase 2 requires R1 reproducible inputs and R2 functional contents; R3 byte identity is measured and reported.
- GitHub Actions executes repository scripts; it does not define the build architecture.
- Privileged workflows never run fork pull-request code and third-party actions use full commit SHAs.
- Cleanup refuses deletion while any build mount remains.
- The live image contains no telemetry, enabled SSH service, or production signing key.
- Automatic installation uses GPT, a FAT32 ESP at `/boot/efi`, and Btrfs subvolumes `@`, `@home`, `@snapshots`, `@cache`, `@log`, with conditional `@swap`.
- Btrfs starts with `defaults,compress=zstd:1`; EFI uses `defaults,umask=0077`.
- Plasma is a validation surface, not the final Felunyx desktop design.
- Static configuration is never reported as Virtual or Hardware proof.

---

### Task 1: Canonicalize Approval and Decisions

**Files:**
- Modify: `DECISIONS.md`
- Modify: `docs/status/phase-2-reproducible-iso.md`
- Modify: `docs/superpowers/specs/2026-08-04-phase-2-reproducible-iso-design.md`

**Interfaces:** Produces accepted decisions `D-105` through `D-129` and an approved specification status.

- [ ] Append 25 accepted decisions covering the committed releng profile, archiso 89-1, replaceable executor, current/frozen builds, R1/R2/R3, UEFI/BIOS policy, Zen/LTS, GRUB/Limine, Calamares 3.3.14, Btrfs layout, minimal Plasma, live-only privileges, no SSH/telemetry/production keys, guarded cleanup, artifacts, trusted workflows, QEMU V gate, semantic installer automation, and explicit H queue.
- [ ] Change the specification header to `**Status:** Approved on 2026-08-04; implementation plan written`.
- [ ] Mark user review approved and point the phase-status document to this plan.
- [ ] Run:

```bash
python - <<'PY'
import re
from pathlib import Path
ids = [int(x) for x in re.findall(r'D-(\d{3})', Path('DECISIONS.md').read_text())]
assert ids == list(range(1, 130))
assert len(ids) == len(set(ids))
print('decision sequence OK')
PY
```

Expected: `decision sequence OK`.
- [ ] Commit: `docs: approve and plan Phase 2 ISO`.

### Task 2: Establish the Validation Harness

**Files:**
- Create: `pyproject.toml`
- Create: `Makefile`
- Create: `tools/lib/common.sh`
- Create: `tests/test_repository_contract.py`

**Interfaces:** Produces `make test`, `make lint`, `make validate`; shell helpers `felunyx_log`, `felunyx_die`, `felunyx_require_command`, `felunyx_realpath`.

- [ ] Write failing tests asserting expected implementation roots exist and every `tools/felunyx-*` script uses `set -Eeuo pipefail`.
- [ ] Add pytest configuration requiring Python 3.11+ and a Makefile whose `validate` target runs shell syntax checks and pytest.
- [ ] Implement the common library:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
felunyx_log(){ printf '[felunyx] %s\n' "$*" >&2; }
felunyx_die(){ printf '[felunyx] error: %s\n' "$*" >&2; exit 1; }
felunyx_require_command(){ command -v "$1" >/dev/null 2>&1 || felunyx_die "required command missing: $1"; }
felunyx_realpath(){ python3 - "$1" <<'PY'
import os,sys
print(os.path.realpath(sys.argv[1]))
PY
}
```

- [ ] Run `python3 -m pytest -q && make lint`.
- [ ] Commit: `test: establish Phase 2 validation harness`.

### Task 3: Lock the Build Environment

**Files:**
- Create: `build/Containerfile`
- Create: `build/environment.lock.json`
- Create: `build/README.md`
- Create: `tools/felunyx-preflight`
- Create: `tests/test_environment_lock.py`

**Interfaces:** `felunyx-preflight --json PATH [--comparison]` emits architecture, kernel, UID, mount capability, loop devices, free bytes/inodes, RAM, CPUs, KVM, QEMU, and OVMF.

- [ ] Write tests requiring `archiso: 89-1`, an immutable `sha256:` base-image digest, and no `:latest` tag.
- [ ] Resolve `docker.io/library/archlinux:base` to an immutable digest and commit it in `environment.lock.json`; no marker or floating tag may remain.
- [ ] Build an Arch image installing `archiso=89-1`, `base-devel`, `edk2-ovmf`, `qemu-desktop`, `libisoburn`, `python`, `python-pytest`, `shellcheck`, `jq`, and `git`.
- [ ] Implement preflight exit codes: `0` success, `2` missing capability, `64` invalid arguments. It proves mount support with a temporary tmpfs, detects loop/KVM/QEMU/OVMF, requires 10 GiB free for one build and 20 GiB for comparison, and writes JSON atomically.
- [ ] Test help, invalid arguments, JSON shape, and root-only behavior in CI.
- [ ] Commit: `build: lock the canonical Phase 2 environment`.

### Task 4: Import and Track `releng`

**Files:**
- Create: `iso/profile/**`
- Create: `iso/upstream/releng.lock.json`
- Create: `tools/sync-releng`
- Create: `tests/test_releng_lock.py`

**Interfaces:** `sync-releng check --source DIR --report PATH`; `sync-releng apply --source DIR --report PATH --yes`.

- [ ] In the pinned environment verify `pacman -Q archiso` equals `archiso 89-1`, then copy `/usr/share/archiso/configs/releng/.` to `iso/profile/` without edits in the import commit.
- [ ] Generate a sorted path-to-SHA-256 lock plus package checksum, import date, and upstream version.
- [ ] Implement `check` as read-only: exit `0` no delta, `3` delta report, `2` invalid source. Implement `apply` only with `--yes`; reject stale reports when source hash changed.
- [ ] Test identical, added, removed, modified, and stale-report cases.
- [ ] Commit: `build: import and track the archiso releng baseline`.

### Task 5: Package Felunyx Identity and Live Policy

**Files:**
- Create: `packages/felunyx-identity/**`
- Create: `packages/felunyx-iso-hooks/**`
- Create: `tests/test_identity.py`

**Interfaces:** Packages `felunyx-identity`, `felunyx-iso-hooks`; marker `/run/felunyx/live`; metadata `/usr/lib/felunyx/build-info.json`.

- [ ] Test `ID=felunyx`, `ID_LIKE=arch`, `PRETTY_NAME="Felunyx OS Phase 2"`, valid build-info JSON, live sudoers mode `0440`, and masked SSH units.
- [ ] Package `/usr/lib/os-release` as canonical and symlink `/etc/os-release`.
- [ ] Generate build metadata from explicit environment variables, never from wall-clock discovery inside the package.
- [ ] Package live user creation, SDDM Plasma Wayland autologin, passwordless sudo only on live media, NetworkManager enablement, live marker, and masked `sshd.service`/`sshd.socket`.
- [ ] Ensure the installer excludes `felunyx-iso-hooks` from the target system.
- [ ] Build in a clean chroot and run `namcap`.
- [ ] Commit: `feat: add Felunyx live identity and policy packages`.

### Task 6: Package and Configure Calamares

**Files:**
- Create: `packages/calamares/PKGBUILD`
- Create: `packages/felunyx-calamares-config/**`
- Create: `installer/calamares/README.md`
- Create: `tests/test_installer_config.py`

**Interfaces:** Packages `calamares` and `felunyx-calamares-config`; installer logs retained as V artifacts.

- [ ] Test the show/exec sequence, absence of tracking, `initialPartitioningChoice: none`, GPT, Btrfs, `/boot/efi`, exact subvolumes, mount options, GRUB, and ESP limits.
- [ ] Build Calamares 3.3.14 from its release tarball, verify the fixed SHA-256 and release signing fingerprint, use Qt 6 and `-DINSTALL_CONFIG=OFF`.
- [ ] Install only the required modules: welcome, locale, keyboard, partition, users, summary, install, finished, mount, fstab, initcpiocfg, bootloader, packages, unpackfs, machineid, services-systemd.
- [ ] Configure Btrfs:

```yaml
btrfsSubvolumes:
  - { mountPoint: /, subvolume: /@ }
  - { mountPoint: /home, subvolume: /@home }
  - { mountPoint: /.snapshots, subvolume: /@snapshots }
  - { mountPoint: /var/cache, subvolume: /@cache }
  - { mountPoint: /var/log, subvolume: /@log }
btrfsSwapSubvol: /@swap
mountOptions:
  - { filesystem: default, options: [ defaults ] }
  - { filesystem: efi, options: [ defaults, umask=0077 ] }
  - { filesystem: btrfs, options: [ defaults, "compress=zstd:1" ] }
  - { filesystem: btrfs_swap, options: [ defaults, noatime ] }
```

- [ ] Configure GRUB with Zen as the stable top-level kernel and LTS visible/selectable; never depend on menu index or translated title.
- [ ] Build both packages in a clean chroot and run installer-config tests.
- [ ] Commit: `feat: package and configure the Felunyx installer`.

### Task 7: Customize the ISO Profile

**Files:**
- Modify: `iso/profile/packages.x86_64`
- Modify: `iso/profile/profiledef.sh`
- Modify: `iso/profile/pacman.conf`
- Modify/Create: `iso/profile/airootfs/**`
- Create: `iso/README.md`
- Create: `tests/test_profile.py`

**Interfaces:** Consumes the local Felunyx repository and produces a valid profile with explicit Zen/LTS boot entries.

- [ ] Test required package inventory, no `openssh`, label/install-dir limits, UEFI modes, separate kernels, and minimal customization-script responsibilities.
- [ ] Include `base`, both kernels, firmware/microcode, `btrfs-progs`, GRUB/EFI tools, NetworkManager, minimal Plasma Wayland, SDDM, Dolphin, Konsole, Calamares, and all Felunyx packages.
- [ ] Set `iso_name=felunyx-os`, `install_dir=felunyx`, Felunyx publisher/application, required UEFI modes, and retained best-effort BIOS mode.
- [ ] Add explicit live entries `Felunyx OS — Linux Zen` and `Felunyx OS — Linux LTS`, Zen first/default.
- [ ] Keep `customize_airootfs.sh` limited to permissions, unit enablement, required cache generation, and SSH-mask validation; user creation, identity, and installer config remain package-owned.
- [ ] Run pytest, `bash -n`, and shellcheck.
- [ ] Commit: `feat: define the Felunyx Phase 2 archiso profile`.

### Task 8: Implement Build Modes and Safe Cleanup

**Files:**
- Create: `tools/felunyx-build`
- Create: `tools/lib/mount_guard.sh`
- Create: `tests/test_cleanup_guard.py`
- Create: `tests/test_build_modes.py`

**Interfaces:** `felunyx-build --mode integration|frozen --output DIR [--archive-date YYYY/MM/DD] [--keep-work]`.

- [ ] Test rejection of `/`, empty path, repository root, symlink-to-root, workdirs outside the temporary root, and deletion while `findmnt` reports mounts.
- [ ] Implement `felunyx_assert_safe_workdir`, `felunyx_list_workdir_mounts`, `felunyx_unmount_recorded`, `felunyx_remove_workdir`; immediately re-run `findmnt --submounts --json --target` before removal.
- [ ] Integration mode uses current mirrors and records resolved versions. Frozen mode requires an Archive date, writes a mirror list containing only that epoch, and cannot fall through to current mirrors.
- [ ] Build order: Calamares, identity, live hooks, Calamares config, `repo-add`, then `mkarchiso`.
- [ ] Publish atomically: ISO, `SHA256SUMS`, `packages.txt`, `build-info.json`, `source-lock.json`, `validation-report.json`, `build.log`.
- [ ] Run cleanup/build-mode tests and shellcheck.
- [ ] Commit: `build: add safe integration and frozen ISO builds`.

### Task 9: Validate and Compare Builds

**Files:**
- Create: `tools/felunyx-validate`
- Create: `tools/felunyx-compare-builds`
- Create: `tests/test_validation_report.py`
- Create: `tests/test_compare_builds.py`
- Create: `docs/operations/phase-2-build.md`

**Interfaces:** `felunyx-validate --profile DIR [--iso PATH] --report PATH`; `felunyx-compare-builds A B --report PATH`; statuses `pass`, `fail`, `not-run`.

- [ ] Test failures for missing LTS, SSH enabled, missing metadata, wrong subvolume, mixed mirrors, private-key-like content, and missing checksum.
- [ ] Validate profile syntax, package inventory, units, permissions, boot entries, identity, installer config, no secrets/SSH.
- [ ] Inspect the ISO read-only and record volume, inventory, kernel/initramfs pairs, boot files, manifest, build metadata, Calamares config, and enabled units.
- [ ] Compare R2 contents while ignoring only documented volatile ISO timestamp/build UUID/filesystem-order metadata; never ignore packages, payload, ownership, boot, kernels, or installer config.
- [ ] Document exact build, frozen, comparison, cleanup-recovery, and report-reading commands.
- [ ] Commit: `test: validate and compare Felunyx ISO builds`.

### Task 10: Add Semantic QEMU/OVMF Tests

**Files:**
- Create: `tools/felunyx-run-vm`
- Create: `tests/boot/expect_serial.py`
- Create: `tests/boot/assert_installed_system.py`
- Create: `tests/installer/drive-installation.py`
- Create: `docs/operations/phase-2-virtual-tests.md`

**Interfaces:** `boot-live`, `install`, and `boot-installed` subcommands accepting ISO/disk/kernel/artifact paths.

- [ ] Define a virtio-serial evidence contract for OS identity, boot ID, running kernel, graphical target, SDDM, Plasma Wayland availability, SSH state, and Calamares markers.
- [ ] Launch QEMU with OVMF code plus a writable vars copy, virtio devices, QMP, KVM when available and TCG fallback with longer timeout.
- [ ] Select live Zen/LTS semantically through bootloader configuration or injected boot selection, never screen coordinates.
- [ ] Automate Calamares only through a supported test/unattended/module interface or stable accessibility object names. If upstream offers none, mark V `blocked` with evidence rather than faking success.
- [ ] Verify installed GRUB, requested kernel, exact Btrfs layout, absence of live-only sudo/autologin, SSH disabled, and build metadata.
- [ ] Add controlled installer failure using a dedicated failing module/profile and require retained logs plus no success marker.
- [ ] Commit: `test: add semantic QEMU and installer validation`.

### Task 11: Add Secure GitHub Actions

**Files:**
- Create: `.github/workflows/validate.yml`
- Create: `.github/workflows/build-iso.yml`
- Create: `.github/workflows/virtual-smoke.yml`
- Create: `tests/test_workflows.py`

**Interfaces:** PRs run unprivileged validation; trusted manual/scheduled/push events run build; virtual smoke consumes trusted artifacts.

- [ ] Test that PR workflows use `contents: read`, no secrets, no privileged mount/container; heavy workflows exclude fork PRs; every `uses:` ends in a 40-character SHA; uploads exclude workdirs/caches; concurrency deduplicates heavy builds.
- [ ] `validate.yml`: checkout, Python/shellcheck, `make validate`, no privilege.
- [ ] `build-iso.yml`: record runner image/resources, safe preflight, pinned environment, chosen mode, validation, upload compact success/failure evidence, no persisted credentials.
- [ ] `virtual-smoke.yml`: UEFI Zen/LTS, then install/installed boots when resources allow; cancellation or missing step is `not-run`, never pass.
- [ ] Run workflow-policy tests.
- [ ] Commit: `ci: add trusted Phase 2 build and virtual validation`.

### Task 12: Complete the Remote Gate

**Files:**
- Create: `docs/evidence/phase-2-remote-gate.md`
- Modify: `docs/status/phase-2-reproducible-iso.md`

- [ ] Run `make validate` from a clean checkout.
- [ ] Probe Archive package availability, select and record one exact date, then run two independent frozen builds using it.
- [ ] Compare the builds; require R1/R2 pass. Record R3 pass or structured non-functional differences.
- [ ] Verify checksums, manifests, source locks, logs, no secrets, and trusted-workflow policy.
- [ ] Mark only evidence-backed R checkboxes complete and link workflow run IDs/artifact hashes.
- [ ] Commit: `test: complete the Phase 2 remote gate`.

### Task 13: Complete the Virtual Gate

**Files:**
- Create: `docs/evidence/phase-2-virtual-gate.md`
- Create: `docs/evidence/phase-2-hardware-queue.md`
- Modify: `docs/status/phase-2-reproducible-iso.md`

- [ ] Boot live Zen through UEFI and collect serial evidence.
- [ ] Boot live LTS through UEFI and collect serial evidence.
- [ ] Install to a new 64 GiB QCOW2 GPT/Btrfs disk through the semantic Calamares harness.
- [ ] Boot installed Zen and LTS through GRUB; inspect subvolumes and live-policy absence.
- [ ] Run failure injection and require actionable retained logs.
- [ ] Record BIOS smoke as pass/fail/not-run without changing required UEFI result.
- [ ] Leave physical USB, firmware, GPU, Wi-Fi, storage, suspend, peripherals, and multi-monitor items open in H queue.
- [ ] Commit: `test: complete the Phase 2 virtual gate`.

### Task 14: Final Verification and Review PR

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `docs/README.md`
- Modify: `docs/status/phase-2-reproducible-iso.md`

- [ ] From a clean checkout run repository validation and reproduce the documented frozen build on a trusted executor.
- [ ] Verify no ISO/large binary, private key, cache, unresolved marker, floating action tag, privileged fork workflow, or docs/command mismatch is committed.
- [ ] State clearly that Phase 2 artifacts are internal development images, not a public release.
- [ ] Invoke `superpowers:requesting-code-review`, address findings, and rerun affected verification.
- [ ] Open a draft PR containing locks, R/V evidence, R3 result, BIOS result, H queue, limitations, artifacts, checksums, and rollback strategy.
- [ ] Stop at the Phase 2 boundary; do not merge or begin Phase 3 without user review.
