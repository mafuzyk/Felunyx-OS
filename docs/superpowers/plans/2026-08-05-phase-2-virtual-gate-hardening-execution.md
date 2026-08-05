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
