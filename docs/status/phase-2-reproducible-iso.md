# Phase 2 Status — Reproducible ISO Skeleton

## Current state

**Design and implementation plan approved; implementation is active in draft work and Phase 2 remains incomplete.**

The Phase 2 reproducible ISO skeleton is implemented and hardened on isolated draft branches rather than integrated into `main`. Remote evidence is partial and still in progress. Virtual validation remains pending a matching rebuilt ISO and runtime evidence. Hardware validation is not required to close Phase 2.

No installable public release exists, and no Remote or Virtual completion claim is made by this status document.

## Goal

Produce a minimal, repeatable, virtually bootable and installable Felunyx skeleton with Linux Zen, Linux LTS fallback, a minimal Plasma Wayland live session, Calamares, Btrfs, and installed GRUB.

## Design and implementation evidence

| Deliverable | Status | Evidence |
|---|---|---|
| Phase 2 specification | Approved | `docs/superpowers/specs/2026-08-04-phase-2-reproducible-iso-design.md` |
| Source ledger | Complete | `docs/research/phase-2-source-ledger.md` |
| ISO structure approach | Approved | Simple `archiso` profile with prepared boundaries |
| Firmware approach | Approved | UEFI required, BIOS best-effort |
| Build environment approach | Approved | Canonical environment, replaceable executor |
| Error-prevention policy | Approved | Primary-source review plus explicit pending V/H tests |
| User review of written specification | Approved — 2026-08-04 | Conversation approval |
| Implementation plan | Complete | `docs/superpowers/plans/2026-08-04-phase-2-reproducible-iso.md` |
| Implementation | Active — draft, incomplete | PR #3 with hardening/fix work in PR #5, #8 and #9; integration and phase review pending |

## Current implementation work

- PR #3 contains the Phase 2 reproducible ISO skeleton implementation and remains draft.
- PR #5 hardens the Virtual gate and remains draft.
- PR #8 fixes blockers in the build and Virtual-gate path and remains draft.
- PR #9 addresses the live initrd/microcode boot-path failure and remains draft.

These branches are evidence of active implementation. They are not evidence that Phase 2 has passed its Remote or Virtual gates.

## Proposed completion gates

The checklists below remain completion requirements. They are intentionally not marked complete merely because related source code or draft evidence exists; completion requires reviewed evidence at the declared gate.

### Remote gate (R)

- [ ] exact environment and source locks committed;
- [ ] `releng` baseline and delta report validated;
- [ ] integration and frozen build modes implemented;
- [ ] package resolution and content checks pass;
- [ ] work-directory cleanup safety tests pass;
- [ ] two frozen builds have equivalent manifests and functional payload;
- [ ] provenance, checksums, logs, and comparison reports produced;
- [ ] no secrets or production signing keys present;
- [ ] privileged workflows restricted to trusted inputs.

**Current claim:** partial/in progress. Source, policy, tests and build work exist in draft branches, but the full Remote gate has not been reviewed as complete.

### Virtual gate (V)

- [ ] UEFI QEMU/OVMF boot reaches the declared live target;
- [ ] Plasma Wayland live session evidence collected;
- [ ] Zen boots as default;
- [ ] LTS boots when selected;
- [ ] Calamares installs to a disposable GPT/Btrfs disk;
- [ ] installed GRUB boots Zen;
- [ ] installed GRUB boots LTS;
- [ ] Btrfs subvolume and mount layout verified;
- [ ] controlled installer failure retains actionable logs;
- [ ] BIOS smoke result recorded when the inherited path remains enabled.

**Current claim:** pending. A matching rebuilt ISO and runtime evidence are still required; Remote/source validation is not Virtual proof.

### Hardware queue (H)

Not required to close Phase 2:

- [ ] physical UEFI USB boot;
- [ ] real graphics and network devices;
- [ ] physical storage installation;
- [ ] firmware variance;
- [ ] suspend/resume and peripherals.

**Current claim:** not required for Phase 2 and not tested as part of this phase gate.

## Review conclusion

The Phase 2 written design and implementation plan were approved on 2026-08-04. Implementation is now active across isolated draft work, but Phase 2 remains open until its required Remote and Virtual evidence is reviewed and the phase boundary is explicitly approved.

The strongest project-level statement supported by this document is therefore:

- **R — Remote:** partial/in progress;
- **V — Virtual:** pending;
- **H — Hardware:** not required to close Phase 2.

## Current review boundary

1. continue Phase 2 implementation and hardening on the existing isolated draft branches;
2. produce a matching trusted build and retained evidence;
3. review the complete Remote and Virtual gates without inferring one from the other;
4. reconcile/integrate the approved Phase 2 branch chain only after those gates are supported;
5. stop at the Phase 2 review boundary for explicit approval before marking the phase complete.
