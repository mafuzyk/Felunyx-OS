# Phase 2 Status — Reproducible ISO Skeleton

## Current state

**Design approved on 2026-08-04; implementation plan written.**

The approved design and executable plan are complete. No ISO implementation is included in this specification branch; implementation begins on a separate isolated branch after this pull request is merged.

## Goal

Produce a minimal, repeatable, virtually bootable and installable Felunyx skeleton with Linux Zen, Linux LTS fallback, a minimal Plasma Wayland live session, Calamares, Btrfs, and installed GRUB.

## Design evidence

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
| Implementation | Ready to start | Separate implementation branch |

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

## Review conclusion

The user approved the Phase 2 written design on 2026-08-04. The implementation plan was produced with exact task boundaries, file ownership, test commands, commit boundaries, Remote/Virtual evidence requirements, and explicit Hardware deferrals.

## Implementation transition

1. merge the approved specification and plan;
2. create `agent/phase-2-implementation` from the new `main`;
3. execute the implementation plan task-by-task;
4. stop at the Phase 2 review boundary with R/V evidence and the H queue.
