# Repository Map

## Current phase

Phase 1 is documentation-first. The repository should not contain empty implementation directories whose architecture has not yet been tested.

Current responsibilities:

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── docs/
│   ├── architecture/
│   ├── product/
│   ├── status/
│   └── superpowers/
│       └── specs/
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── DECISIONS.md
├── LICENSE
├── PHILOSOPHY.md
├── README.md
├── ROADMAP.md
├── SECURITY.md
└── VISION.md
```

## Planned implementation areas

Directories are added when their owning phase begins.

### `iso/`

Owns image composition and installer integration:

- build definition;
- live environment;
- package manifests;
- Calamares modules and branding;
- bootloader integration;
- image metadata.

### `packages/`

Owns Felunyx package recipes and repository metadata:

- native packages;
- integration packages;
- justified patches;
- signing and catalog metadata;
- package tests.

Package build infrastructure may later move to a separate restricted repository when signing access requires it.

### `profiles/`

Owns desktop-profile integration:

```text
profiles/
├── kde/
├── xfce/
└── hyprland/
```

Each profile consumes shared platform contracts and declares capability differences.

### `platform/`

Rust workspace for desktop-independent services and libraries.

Probable responsibility groups, subject to Phase 3 specification:

- configuration and schema;
- package catalog;
- transaction planner;
- risk;
- snapshot orchestration;
- action journal;
- system health;
- session/Sets/rules;
- typed IPC.

Crate names are intentionally deferred until boundaries are validated.

### `desktop/`

Native Felunyx Desktop:

```text
desktop/
├── compositor/
├── shell/
├── settings/
├── central/
├── greeter/
└── ui/
```

This shape can change after the prototype. It is a responsibility map, not a frozen package layout.

### `tools/`

Build, validation, release, migration, and developer utilities that do not belong to one product component.

### `tests/`

Cross-component tests:

- image boot;
- installer;
- update and rollback;
- recovery;
- profile integration;
- hardware or protocol fixtures;
- migration.

Component-local unit tests remain beside their component.

## Repository split criteria

A component moves to another repository only when at least one is true:

- release cadence is materially independent;
- access must be restricted, such as signing infrastructure;
- issue and review ownership are distinct;
- repository size or CI cost harms normal work;
- upstream collaboration requires an independent project identity.

Splitting is not used merely to make an architecture diagram look sophisticated.

## Source-of-truth rules

- `DECISIONS.md` records accepted direction.
- Root architecture documents define cross-project contracts.
- Detailed product documents define behavior.
- Component specifications define implementable interfaces.
- Implementation plans define task sequence.
- Tests define executable behavior.
- Generated files do not become the only source of truth.
