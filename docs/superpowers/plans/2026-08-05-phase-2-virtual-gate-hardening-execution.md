# Phase 2 Virtual Gate Hardening — Execution Ledger

**Date:** 2026-08-05

**Branch:** `fix/phase-2-virtual-gate-hardening`

**Base:** `agent/phase-2-implementation` at `1f89d17b10c8e0b4965a7f8ebc5e4d509e5f637a`

**Owning PR:** #5

This ledger records implementation evidence and narrow corrections discovered while executing `2026-08-05-phase-2-virtual-gate-hardening.md`. It does not change accepted product decisions or promote Remote, Virtual, or Hardware gates beyond available evidence.

## Parallel-work boundary

Draft PR #6 (`docs/work-environments-design`) is isolated preparatory design based on `main`. This branch does not consume, rebase onto, or modify that work. `docs/README.md` is reserved for later explicit reconciliation because PR #6 already changes it.

## Task 1 — Version and strengthen live evidence

**Status:** implemented and validated remotely on 2026-08-05.

Implemented:

- schema 2 `FELUNYX_EVIDENCE` payload;
- explicit build-metadata, UEFI, graphical-target, SDDM, NetworkManager, Plasma Wayland, session, and SSH service/socket observations;
- active local Plasma Wayland session discovery through `loginctl`;
- strict host-side validation with malformed, duplicate, partial, and false-state rejection;
- atomic validated-evidence persistence;
- opt-in guest collection restricted to live media;
- a 120-second session observation budget and a 150-second systemd start timeout.

### Narrow execution correction

Task 1 Step 3 originally showed:

```ini
After=graphical.target display-manager.service
Wants=display-manager.service
```

That ordering is superseded by the implementation below:

```ini
Wants=display-manager.service
After=display-manager.service

[Install]
WantedBy=graphical.target
```

The package installs the enablement symlink in `graphical.target.wants`. A service pulled in by a target receives target ordering through systemd's target dependency semantics; adding `After=graphical.target` to that same service would oppose the target's normal ordering and risk a cycle. Runtime readiness is therefore observed inside the collector for up to 120 seconds rather than represented by a circular target dependency.

### TDD evidence

- Baseline: validation run #70 passed before Task 1 changes.
- RED run #73: 13 new failures, 55 prior tests passed; strict output/schema behavior absent.
- RED run #75: 1 failure, 68 passed; only guest schema 2 remained absent.
- RED run #77: 2 failures, 68 passed; guest schema and service-target contracts absent.
- RED run #78: 3 failures, 68 passed; guest schema, service ordering, and timeout contracts absent.
- GREEN run #81 (`31002594336`): 71 tests passed in 1.83 seconds.

### Validation level

- **R — Remote:** Task 1 source, schema, policy, packaging, and static tests passed.
- **V — Virtual:** pending a matching rebuilt ISO and runtime evidence review.
- **H — Hardware:** not tested.

The development ISO from run `30951476281` predates these guest-side changes and cannot inherit their validation.

## Task 2 — Select live kernels through verified OVMF variables

**Status:** implemented and validated remotely on 2026-08-05.

Implemented:

- exact allowlist for `felunyx-linux-zen.conf` and `felunyx-linux-lts.conf`;
- offline `LoaderEntryOneShot` modification in a scenario-owned OVMF varstore;
- exact GUID, attributes, UTF-16LE value, and readback validation;
- atomic varstore replacement only after verified readback;
- atomic tool/version/entry report;
- removal of timed QMP `down`/`ret` navigation;
- `python3-virt-firmware` installation and version capture in the Virtual executor;
- explicit fail-closed blocking of installed boots until Tasks 3 and 4 provide installed evidence and semantic GRUB selection.

### Narrow execution correction

Task 2 Step 3 described the JSON `data` field as Base64. The pinned `virt-fw-vars` contract uses a hexadecimal byte string. The implementation therefore serializes the NUL-terminated UTF-16LE entry identifier with `.hex()` and rejects malformed, wrong-GUID, wrong-attribute, missing, duplicate, or mismatched readback.

Input shape:

```json
{
  "variables": [
    {
      "name": "LoaderEntryOneShot",
      "guid": "4a67b082-0a4c-41cf-b6c7-440b29bb8c4f",
      "attr": 7,
      "data": "<hexadecimal UTF-16LE bytes>"
    }
  ]
}
```

### TDD evidence

- RED run #84 (`31003084640`): 6 new failures, 71 prior tests passed; helper, semantic integration, and executor dependency were absent.
- GREEN run #88 (`31003319097`): 77 tests passed in 2.10 seconds.

### Validation level

- **R — Remote:** Task 2 helper, input/readback contract, harness policy, workflow dependency, and static tests passed.
- **V — Virtual:** pending execution against a matching rebuilt ISO and OVMF varstore on the Virtual runner.
- **H — Hardware:** not tested.

## Task 3 — Inspect installed GRUB, kernels, Btrfs, and live-policy absence

**Status:** implemented and validated remotely on 2026-08-05.

Implemented:

- an opt-in installed-system collector that exits silently on live media;
- read-only package checks for GRUB, Linux Zen, Linux LTS, and absence of `felunyx-iso-hooks`;
- non-empty GRUB configuration and both installed kernel image observations;
- exact runtime mounts for `@`, `@home`, `@snapshots`, `@cache`, and `@log`;
- Btrfs subvolume inventory and persistent `/etc/fstab` evidence;
- `compress=zstd:1` and EFI mask validation, accepting `umask=0077` or equivalent `fmask` plus `dmask`;
- build metadata and UEFI observations;
- absence of the live marker, live sudo policy, and live SDDM autologin;
- separate SSH service and socket observations;
- duplicate, malformed, partial, wrong-kernel, wrong-filesystem, wrong-subvolume, missing-package, and policy-residue rejection;
- installed Zen boot integration through the strict host assertion;
- continued fail-closed blocking of installed LTS until Task 4 provides semantic GRUB one-shot selection.

### Narrow execution correction

The installed-evidence tests were placed in `tests/test_installed_evidence.py` instead of further expanding `tests/test_virtual_harness.py`. This keeps the live/OVMF and installed-storage contracts independently reviewable while preserving the same repository-wide pytest gate.

The inspector performs only read operations. It does not install packages, regenerate GRUB, create subvolumes, remount filesystems, enable services, or repair the target.

### TDD evidence

- RED run #92 (`31003732051`): 18 new failures, 77 prior tests passed; installed assertion, collector, packaging, and harness integration were absent.
- GREEN run #97 (`31004021318`): 95 tests passed in 2.78 seconds.

### Validation level

- **R — Remote:** Task 3 schema, rejection policy, read-only source contract, package/service integration, and static tests passed.
- **V — Virtual:** pending installed runtime evidence from a matching rebuilt ISO and disk.
- **H — Hardware:** not tested.

## Task 4 — Select installed LTS through verified GRUB one-shot state

**Status:** implemented and validated remotely on 2026-08-05.

Implemented:

- parsing of the generated `grub.cfg` by structural `submenu` and `menuentry` blocks;
- exact identification of the entry that loads `/boot/vmlinuz-linux-lts`;
- rejection of missing IDs, duplicate LTS entries, numeric selectors, visible titles, and ambiguous selectors;
- hierarchical selector construction as `submenu_id>entry_id`;
- opt-in preparation restricted to installed systems and the exact `linux-lts` fw_cfg request;
- `grub-reboot` invocation with `grub-editenv` readback of the exact `next_entry` value;
- atomic `FELUNYX_GRUB_NEXT` evidence and explicit poweroff after verified preparation;
- host-side rejection of malformed, duplicate, unverified, non-LTS, numeric, or non-hierarchical evidence;
- `boot-installed --kernel zen --prepare-next lts` as the only preparation path;
- an ordinary follow-up `boot-installed --kernel lts` on the same disk, with no QMP menu input.

### Narrow execution correction

Task 3's temporary assertion that installed LTS must remain blocked was superseded only after every Task 4 contract was present. The first GREEN attempt reached 107 passing tests and failed solely on that intentionally obsolete expectation. Updating the assertion did not remove or weaken the new GRUB one-shot tests.

The preparer changes only GRUB's one-boot `next_entry` state. It does not change `GRUB_DEFAULT`, write a persistent default, use `grub-set-default`, or match a translated display title.

### TDD evidence

- RED run #100 (`31004290945`): 13 new failures, 95 prior tests passed; guest preparer, host assertion, package/service integration, and harness handoff were absent.
- Intermediate run #105 (`31004629375`): 107 tests passed; one superseded Task 3 blocking assertion failed.
- GREEN run #106 (`31004731971`): 108 tests passed in 3.62 seconds.

### Validation level

- **R — Remote:** Task 4 parser, selector policy, one-shot state contract, package/service integration, harness handoff, and static tests passed.
- **V — Virtual:** pending execution of Zen preparation and the subsequent LTS boot on a matching installed disk.
- **H — Hardware:** not tested.

## Task 5 — Inject and retain a controlled Calamares failure

**Status:** implemented and validated remotely on 2026-08-05.

Implemented:

- an isolated Calamares settings overlay under `/usr/lib/felunyx/tests/calamares-failure/`;
- the production show and execution sequence with exactly one inserted `felunyx-fail` job after `bootloader` and before `umount`;
- a Python job returning the exact `FelunyxInjectedFailure` classification;
- explicit `success` and `failure` fw_cfg modes;
- production Calamares invocation unchanged in success mode;
- alternate `-c` settings only in failure mode;
- separate `start`, `stage`, `success`, `failure`, and `blocked` events;
- rejection of accidental success, unrelated failure, process crash, inaccessible AT-SPI object, and timeout;
- retention of harness, Calamares debug, session, and system logs before poweroff.

### Narrow execution correction

The first GREEN source run reached 112 passing tests and failed only because one test searched for a same-line `emit('failure'` substring. The test was strengthened to inspect Python AST call arguments and require all five event classes structurally, without changing production behavior.

The exact AT-SPI names presented by the Calamares failure dialog remain runtime assumptions until a matching ISO executes this scenario. Source validation cannot prove that accessibility surface.

### TDD evidence

- RED run #108 (`31005042763`): 5 new failures, 108 prior tests passed; overlay, module, package isolation, and driver classification were absent.
- Intermediate run #113 (`31005254376`): 112 tests passed; one formatting-dependent test failed.
- GREEN run #114 (`31005420817`): 113 tests passed in 3.16 seconds.

### Validation level

- **R — Remote:** Task 5 overlay, module contract, package isolation, event classification, log-retention source paths, and static tests passed.
- **V — Virtual:** pending Calamares execution, AT-SPI observation, expected failure, transported logs, and artifact review on a matching ISO.
- **H — Hardware:** not tested.

## Task 6 — Make QEMU scenarios explicit and fail closed

**Status:** implemented and validated remotely on 2026-08-05.

Implemented:

- independent `boot-live`, `install`, `boot-installed`, and `boot-bios` commands;
- mandatory `success` or `failure` installation mode;
- fresh-disk enforcement for both installation paths;
- atomic `scenario-result.json` records with `pass`, `fail`, `blocked`, or `not-run` vocabulary;
- exit traps that preserve available evidence and never convert interruption into pass;
- scenario-owned OVMF variables, QMP socket, serial log, stderr log, and guest-evidence stream;
- read-only QMP status/version diagnostics;
- a dedicated virtio-serial port named `org.felunyx.evidence`;
- Base64 log transport with safe-name, byte-count, and SHA-256 verification before host extraction;
- exact success/failure installer outcome assertions;
- required actionable logs for controlled failure;
- separate strict BIOS evidence that requires `uefi=false` while retaining every other live-session assertion;
- operational documentation for manual reproduction and evidence review.

### Narrow execution correction

Task 5 originally retained logs only inside the volatile live guest. Task 6 adds a dedicated virtio-serial transport so retained logs become host artifacts before the guest powers off. This avoids guest mounts and does not alter the installed target.

`boot-bios` remains best-effort. Its scenario result is structured, but it cannot replace or weaken UEFI requirements.

### TDD evidence

- RED run #118 (`31005699837`): 12 new failures, 113 prior tests passed; result writer, installer outcome validator, BIOS mode, transport, and scenario lifecycle were absent.
- GREEN run #122 (`31006272291`): 125 tests passed in 8.59 seconds.

### Validation level

- **R — Remote:** Task 6 CLI contracts, atomic results, strict outcome/log parsing, BIOS policy, shell syntax/lint, diagnostics paths, and static tests passed.
- **V — Virtual:** pending runtime execution of all commands against a matching trusted artifact.
- **H — Hardware:** not tested.
