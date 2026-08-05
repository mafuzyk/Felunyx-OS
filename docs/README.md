# Felunyx Documentation

This directory contains detailed product, architecture, governance, specification, research, implementation-plan, and phase-status material.

Root documents define the project-wide contract:

- [Vision](../VISION.md)
- [Philosophy](../PHILOSOPHY.md)
- [Architecture](../ARCHITECTURE.md)
- [Decision register](../DECISIONS.md)
- [Roadmap](../ROADMAP.md)
- [Contributing](../CONTRIBUTING.md)
- [Security](../SECURITY.md)

## Product specifications

- [Desktop experience](product/desktop-experience.md)
- [Central and package management](product/central-and-packages.md)
- [Recovery and snapshots](product/recovery-and-snapshots.md)
- [Sets, sessions, rules, workspaces, and monitors](product/sets-sessions-rules.md)
- [Installer and first boot](product/installer-and-first-boot.md)

## Architecture

- [Native Felunyx Desktop](architecture/felunyx-desktop.md)
- [Repository map](architecture/repository-map.md)

## Process

- [Remote, Virtual, and Hardware validation gates](process/validation-gates.md)

## Superpowers specifications

- [Phase 1 foundation design](superpowers/specs/2026-08-03-felunyx-foundation-design.md)
- [Phase 2 reproducible ISO design](superpowers/specs/2026-08-04-phase-2-reproducible-iso-design.md)
- [Work Environments design — proposed isolated preparation](superpowers/specs/2026-08-05-work-environments-design.md)

## Superpowers implementation plans

- [Phase 2 reproducible ISO implementation plan](superpowers/plans/2026-08-04-phase-2-reproducible-iso.md)

## Research

- [Phase 2 source ledger](research/phase-2-source-ledger.md)

## Status

- [Phase 1 foundation](status/phase-1-foundation.md)
- [Phase 2 reproducible ISO](status/phase-2-reproducible-iso.md)
- [Work Environments isolated preparation](status/work-environments-preparation.md)

## Documentation rules

- Canonical decisions belong in [DECISIONS.md](../DECISIONS.md).
- Product documents explain behavior and experience.
- Architecture documents explain boundaries, ownership, interfaces, data flow, and failure containment.
- Plans explain implementation sequence and are written only after their specification is approved.
- Status documents record evidence against phase exit criteria.
- A roadmap item is not a shipped feature.
- Deferred decisions must name the phase or evidence that will resolve them.
