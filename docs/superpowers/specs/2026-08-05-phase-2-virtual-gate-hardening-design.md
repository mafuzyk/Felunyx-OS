# Felunyx OS Phase 2 — Virtual Gate Hardening Design

**Date:** 2026-08-05

**Status:** Approved by Mafu on 2026-08-05; implementation plan written

**Owning phase:** Phase 2 — Reproducible ISO Skeleton

**Base:** `agent/phase-2-implementation` at `1f89d17b10c8e0b4965a7f8ebc5e4d509e5f637a`

**Working branch:** `fix/phase-2-virtual-gate-hardening`

**Implementation plan:** `docs/superpowers/plans/2026-08-05-phase-2-virtual-gate-hardening.md`

## 1. Purpose

Harden the Phase 2 virtual validation harness so that a successful smoke run proves the declared Virtual gate instead of merely proving that the guest emitted a minimally valid JSON marker.

The work remains inside Phase 2. It does not begin Phase 3, redesign the ISO architecture, introduce public APIs, or describe the existing development image as usable or validated.

The current ISO artifact from workflow run `30951476281` remains unchanged. Any harness change that must be present inside the guest requires a later rebuilt artifact and cannot retroactively validate that image.

## 2. Authority and constraints

This design implements the accepted Phase 2 specification and plan without changing project decisions.

Applicable decisions include:

- D-005: Linux Zen is default and Linux LTS is fallback;
- D-006: automatic installations use Btrfs with separated system and home scopes;
- D-075: no silent repair or hidden state-changing process;
- D-102: completion claims name the strongest R/V/H gate actually passed;
- D-103: isolated preparatory work is allowed while a V gate is unavailable;
- D-104: static conformity is never reported as runtime proof.

The Phase 2 plan additionally requires semantic kernel selection, observable graphical-session evidence, installed GRUB and kernel validation, exact Btrfs layout validation, absence of live-only policy, controlled installer failure, retained logs, and `not-run` rather than false success when a scenario does not execute.

## 3. Current gaps

The current implementation has useful foundations but does not yet satisfy the full contract:

1. `felunyx-evidence` reports graphical target, SDDM, NetworkManager, kernel, live state, identity, and SSH state.
2. `expect_serial.py` currently rejects wrong identity, kernel, live state, or active SSH, but does not require graphical target, SDDM, NetworkManager, or Plasma Wayland availability.
3. Live LTS selection currently waits two seconds and sends `down` and `ret` through QMP. This depends on menu timing and ordering rather than an explicit entry identifier.
4. Installed boots verify only the generic serial marker and running kernel. They do not prove installed GRUB, both kernel payloads, exact Btrfs layout, build metadata, or absence of live-only policy.
5. The workflow groups multiple scenarios into large steps and uploads only matching log files. One early failure can prevent later scenarios and omit useful non-log evidence.
6. Controlled installer failure and actionable retained failure evidence are not implemented.
7. `docs/status/phase-2-reproducible-iso.md` still describes implementation as ready to start.

## 4. Approaches considered

### Approach A — Assertion-only patch

Add checks for `graphical_target`, SDDM, and NetworkManager to the existing parser while retaining timed QMP key presses and the generic installed marker.

Advantages:

- smallest change;
- no new guest evidence fields.

Disadvantages:

- live LTS selection remains timing-dependent;
- installed storage and bootloader claims remain unproven;
- failure injection remains absent;
- a green workflow would still be weaker than the approved Virtual gate.

**Decision:** rejected as insufficient.

### Approach B — Structured gate contract

Version the internal evidence schema, select live entries through the systemd-boot one-shot entry interface, split live and installed assertions, add a dedicated installed-system inspector, add controlled installer failure, and make the workflow summarize every scenario explicitly.

Advantages:

- maps directly to the approved gate;
- failures identify the missing property;
- avoids screen coordinates and menu timing;
- preserves evidence from partial runs;
- remains internal to Phase 2.

Disadvantages:

- requires a new ISO build when guest-side evidence changes;
- adds focused test code and a small executor dependency for editing OVMF variables.

**Decision:** selected.

### Approach C — Screenshot or vision-driven GUI validation

Capture frames and infer the boot menu, Plasma session, and Calamares progress visually.

Advantages:

- resembles manual observation;
- can produce visually persuasive artifacts.

Disadvantages:

- brittle across resolution, rendering, translation, theme, and timing;
- risks coordinate clicking;
- does not prove storage or installed policy;
- adds complexity without replacing structured evidence.

**Decision:** rejected for the gate. Optional screenshots may supplement, never replace, structured evidence.

## 5. Design

### 5.1 Evidence schema

The internal `FELUNYX_EVIDENCE=` payload moves from schema 1 to schema 2. This is a test-only contract and is not a public Felunyx API.

Common required fields:

- `schema` equal to `2`;
- Felunyx identity and immutable build metadata presence;
- running kernel and normalized variant (`zen` or `lts`);
- `live` state;
- `graphical_target`;
- `sddm`;
- Plasma Wayland session availability;
- NetworkManager state;
- SSH service and socket state;
- boot mode identified as UEFI for required scenarios.

Live assertions require:

- `live: true`;
- graphical target active;
- SDDM active;
- an active local user session with `Type=wayland` and KDE/Plasma desktop identity;
- Plasma Wayland session definition and executable available;
- NetworkManager active;
- SSH service and socket inactive;
- requested kernel variant running.

Installed assertions require:

- `live: false`;
- requested kernel variant running;
- GRUB package and generated configuration present;
- Linux Zen and Linux LTS kernel payloads present;
- expected build metadata present;
- live marker absent;
- live-only sudo and SDDM autologin policy absent;
- `felunyx-iso-hooks` absent from the installed package set;
- SSH service and socket inactive;
- Btrfs subvolume `@` mounted at `/`;
- Btrfs subvolume `@home` mounted at `/home`;
- Btrfs subvolume `@snapshots` mounted at `/.snapshots`;
- Btrfs subvolume `@cache` mounted at `/var/cache`;
- Btrfs subvolume `@log` mounted at `/var/log`;
- conditional `@swap` recorded when swapfile support is selected;
- `/boot/efi` mounted from the FAT32 ESP;
- Btrfs mounts expose `compress=zstd:1` and EFI exposes `umask=0077` or its normalized equivalent.

Missing fields, unknown values, malformed JSON, timeout, or mismatched expectations fail the scenario. They are never interpreted as pass.

### 5.2 Semantic live-kernel selection

The harness stops using `sleep 2` plus positional key presses.

For each VM invocation it creates a fresh writable copy of the OVMF variable store. The requested systemd-boot entry identifier is written to the Boot Loader Interface one-shot variable before QEMU starts:

- Zen: `felunyx-linux-zen.conf` when explicit selection is required;
- LTS: `felunyx-linux-lts.conf`.

The implementation uses the standard `LoaderEntryOneShot` variable in the systemd boot-loader vendor namespace. Ubuntu 24.04's `python3-virt-firmware` package supplies `virt-fw-vars` for offline varstore modification. The helper must read the modified variable store back and confirm the requested identifier before QEMU launches.

If the pinned executor cannot create and verify the one-shot variable, the scenario is `blocked` and the workflow fails. It must not fall back silently to timed arrow keys.

The guest serial evidence must still confirm the running kernel. Variable injection alone is not success.

### 5.3 Installed-system inspector and GRUB selection

A focused guest-side inspector produces a structured installed-system payload rather than overloading the generic readiness marker.

The inspector collects read-only evidence using system interfaces and package metadata:

- `uname`;
- `/usr/lib/os-release` and Felunyx build metadata;
- `pacman` package presence for GRUB, Linux Zen, and Linux LTS;
- `/boot/grub/grub.cfg` and both kernel images;
- `findmnt` JSON for root, home, snapshots, cache, log, and ESP;
- Btrfs subvolume inventory;
- `/etc/fstab` entries and mount options;
- systemd states for SDDM, NetworkManager, SSH service, and SSH socket;
- absence of live-only files, package, sudo policy, and autologin configuration.

The host-side assertion validates exact expected values and writes the parsed JSON into the scenario artifact directory.

The inspector performs no repair and changes no guest state.

The installed Zen boot is the default GRUB path. To select installed LTS without menu timing, a separate helper runs only under an explicit test fw_cfg marker after Zen evidence has been emitted. It parses `/boot/grub/grub.cfg`, identifies the LTS menuentry and enclosing submenu by their internal `--id` values and kernel command, calls `grub-reboot` with that ID selector, verifies `next_entry` through `grub-editenv`, emits structured preparation evidence, and powers off. The following boot must reach LTS through GRUB and consume the one-shot state. Display titles, translated strings, numeric indexes, and QMP navigation are forbidden.

### 5.4 Installer success and controlled failure

Normal installation remains driven through stable AT-SPI object names. Coordinate clicking remains forbidden.

A separate explicit fw_cfg test marker enables failure injection. In that mode the harness uses a test-only Calamares configuration overlay containing a deterministic failing execution step after logs and target context exist but before success can be reported.

The failure scenario passes only when all of these are true:

- Calamares reports failure or exits unsuccessfully;
- no installation-success marker exists;
- the serial stream contains a failure marker with stage and error class;
- Calamares debug log and harness log are retained;
- the workflow uploads the failure evidence even though the scenario intentionally failed;
- the target disk is not reused as a successful installation.

Unexpected success is a gate failure.

### 5.5 Workflow orchestration

`Virtual Phase 2 smoke` runs independent named scenarios:

1. live UEFI Zen;
2. live UEFI LTS;
3. install to a fresh 64 GiB QCOW2 disk;
4. installed UEFI/GRUB Zen and verified LTS one-shot preparation;
5. installed UEFI/GRUB LTS;
6. controlled installer failure;
7. BIOS best-effort smoke when enabled.

Required scenarios use `continue-on-error: true` only so later evidence can still be collected. A final summary step evaluates every recorded outcome and fails the job unless all required scenarios passed. Missing, skipped, cancelled, or unrecorded required scenarios become `not-run`, never pass.

The workflow uploads:

- serial logs;
- QEMU stderr and QMP diagnostics;
- parsed live and installed JSON evidence;
- installer and accessibility-harness logs;
- Btrfs and mount reports;
- GRUB one-shot preparation evidence;
- failure-injection evidence;
- final gate summary JSON.

BIOS remains pass/fail/not-run and cannot change the required UEFI result.

### 5.6 Status documentation

`docs/status/phase-2-reproducible-iso.md` will be updated to state:

- implementation exists on PR #3;
- one development ISO artifact was produced by run `30951476281`;
- that artifact is not a public or stable release;
- Remote evidence is incomplete until all R requirements, including comparison evidence, are reviewed;
- Virtual is pending until the hardened workflow executes successfully and its artifacts are reviewed;
- Hardware is not tested;
- PR #3 remains draft and unmerged.

No checkbox is marked complete solely because code or configuration exists.

## 6. Error handling

- All evidence writes are atomic where they persist to disk.
- Guest evidence includes a schema version and rejects partial payloads.
- Timeouts include the tail of relevant serial and process logs.
- QEMU termination preserves artifacts before cleanup.
- OVMF vars are unique per scenario and never shared across concurrent boots.
- A malformed or unverifiable EFI one-shot selection stops before QEMU boot.
- GRUB one-shot preparation is explicit, verified, one-use, and never changes the persistent default.
- Installer automation emits `start`, stage transitions, `success`, `failure`, or `blocked`; ambiguous termination is failure.
- Cleanup removes only scenario-owned temporary files and never deletes a mounted work tree.

## 7. Testing strategy

Implementation follows tests first or alongside each change.

Static tests will require:

- schema 2 fields and strict live/installed assertions;
- rejection of missing graphical, SDDM, active Plasma session, NetworkManager, GRUB, kernel, Btrfs, metadata, or policy evidence;
- no timed `sleep 2` plus `down`/`ret` kernel-selection path;
- verified systemd-boot one-shot entry IDs;
- verified GRUB one-shot LTS entry IDs and `grubenv` readback;
- exact installed Btrfs subvolume and mount expectations;
- retained controlled-failure evidence and no false success marker;
- independent workflow scenarios plus final outcome summary;
- pinned third-party actions and read-only permissions;
- honest status wording with R/V/H distinctions.

Remote validation commands:

```bash
python3 -m pytest -q
make lint
make validate
```

A green Remote validation proves source and policy consistency only. It does not prove Virtual behavior.

Virtual validation requires a newly built trusted artifact containing the guest-side changes, followed by the hardened workflow and review of all uploaded evidence.

## 8. Expected files

Likely modified files:

- `packages/felunyx-identity/felunyx-evidence`;
- `packages/felunyx-identity/felunyx-evidence.service`;
- `packages/felunyx-identity/PKGBUILD`;
- `packages/felunyx-iso-hooks/drive-installation.py`;
- `tests/boot/expect_serial.py`;
- `tools/felunyx-run-vm`;
- `.github/workflows/virtual-smoke.yml`;
- `tests/test_virtual_harness.py`;
- `tests/test_workflows.py`;
- `docs/status/phase-2-reproducible-iso.md`.

Likely new focused files:

- `tests/boot/set_loader_oneshot.py`;
- `tests/boot/assert_installed_system.py`;
- `tests/boot/assert_grub_oneshot.py`;
- `tests/boot/write_scenario_result.py`;
- `packages/felunyx-identity/felunyx-installed-evidence`;
- `packages/felunyx-identity/felunyx-prepare-grub-oneshot`;
- installer failure-injection configuration owned by `felunyx-iso-hooks`;
- unit-test fixtures for valid and invalid evidence.

The implementation plan may reduce this list only when an existing file cleanly owns the responsibility. Unrelated refactoring is out of scope.

## 9. Completion and review boundary

This hardening work is complete only when:

- source tests and lint pass;
- the implementation is reviewed on isolated draft PR #5 targeting `agent/phase-2-implementation`;
- no false V claim is introduced;
- rollback is a clean revert of the focused hardening commits;
- a new ISO build is identified as required because guest payload changes;
- the user reviews the changes before they are integrated into PR #3.

Even after source completion, the Virtual gate remains pending until the hardened workflow runs against the matching rebuilt ISO and its evidence is reviewed. Phase 3 remains blocked.