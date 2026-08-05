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
