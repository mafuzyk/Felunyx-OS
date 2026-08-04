# Phase 2 Status — Reproducible ISO Skeleton

## Current state

**Design written and self-reviewed; awaiting user review.**

No ISO profile, package recipe, build container, workflow, or production implementation has been created. This is intentional: the Superpowers design gate requires approval of the written specification before implementation planning.

## Goal

Produce a minimal, repeatable, virtually bootable and installable Felunyx skeleton with Linux Zen, Linux LTS fallback, a minimal Plasma Wayland live session, Calamares, Btrfs, and installed GRUB.

## Design evidence

| Deliverable | Status | Evidence |
|---|---|---|
| Phase 2 specification | Complete | `docs/superpowers/specs/2026-08-04-phase-2-reproducible-iso-design.md` |
| Source ledger | Complete | `docs/research/phase-2-source-ledger.md` |
| ISO structure approach | Approved | Simple `archiso` profile with prepared boundaries |
| Firmware approach | Approved | UEFI required, BIOS best-effort |
| Build environment approach | Approved | Canonical environment, replaceable executor |
| Error-prevention policy | Approved | Primary-source review plus explicit pending V/H tests |
| User review of written specification | Pending | Phase gate |
| Implementation plan | Blocked | Written only after specification approval |
| Implementation | Not started | Correct for current gate |

## Proposed completion gates

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

### Hardware queue (H)

Not required to close Phase 2:

- [ ] physical UEFI USB boot;
- [ ] real graphics and network devices;
- [ ] physical storage installation;
- [ ] firmware variance;
- [ ] suspend/resume and peripherals.

## Review guide

Recommended order:

1. Executive summary and goals in the Phase 2 specification.
2. Sections 5–7: approved approaches and validation/reproducibility model.
3. Sections 9–12: `releng`, build modes, environment, and cleanup safety.
4. Sections 15–21: boot, kernels, GRUB, Calamares, Btrfs, and KDE skeleton.
5. Sections 23–26: tests, workflow security, and error handling.
6. Section 27: proposed decisions.
7. Source ledger for any decision that needs traceability.

## Phase boundary

After user approval:

1. convert proposed Phase 2 decisions into canonical decision entries;
2. invoke the Superpowers `writing-plans` skill;
3. write the implementation plan with exact files, commands, tests, checkpoints, and commit boundaries;
4. begin implementation only after the plan exists.
