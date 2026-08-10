# Felunyx OS Architecture

## Status

This document defines the target architecture approved during Phase 1 and updated by later accepted decisions. It is intentionally implementation-oriented enough to guide later plans, while avoiding invented APIs before their owning phase begins.

## Architectural shape

Felunyx is a **phased monorepo and layered distribution platform**.

The distribution can ship before the native Felunyx Desktop is complete. KDE Plasma is the first reference desktop, while XFCE and Hyprland join after the shared platform stabilizes. The native desktop is a parallel long-term track built on the same services rather than a separate operating system.

The architecture is divided into four layers:

1. **Distribution foundation**
2. **Felunyx platform**
3. **Desktop experiences**
4. **Delivery and recovery infrastructure**

Each layer has explicit responsibilities and failure boundaries.

## 1. Distribution foundation

The foundation owns the bootable and installable system:

- Arch Linux package base;
- `systemd`;
- Linux Zen default kernel;
- Linux LTS fallback kernel;
- Btrfs subvolume layout;
- bootloader configuration;
- Calamares integration;
- hardware enablement and firmware;
- official package repository configuration;
- ISO generation and reproducibility metadata.

### Filesystem model

The automatic installation uses Btrfs with at least:

- a system root subvolume;
- a separate home subvolume;
- dedicated snapshot locations;
- subvolumes needed to exclude volatile or cache-heavy paths from snapshots.

The exact subvolume names are selected during the ISO implementation phase and become stable interfaces once shipped.

System restoration preserves home by default. A home restoration first creates a safety snapshot of the current home state.

### Kernel and boot model

Linux Zen is the default boot target. Linux LTS is installed and maintained as a fallback.

The installer presents exactly one bootloader choice:

- **GRUB** — default and recommended;
- **Limine** — official alternative.

Only the selected bootloader is installed. Boot failure never silently chooses a recovery action after a timeout; it asks the person what to do.

## 2. Felunyx platform

The platform is desktop-agnostic. It exposes domain services used by KDE, XFCE, Hyprland, the future Felunyx Desktop, the CLI, and recovery tools.

### Platform responsibilities

- package source catalog and policy;
- transaction planning and execution;
- risk classification;
- snapshot orchestration;
- reboot-pending state;
- system health;
- configuration inheritance;
- application rules;
- Sets and session restoration;
- monitor and workspace identity;
- notification policy integration;
- action history and recovery metadata;
- privilege boundaries;
- typed service APIs.

### Service model

Platform logic is written primarily in Rust. Services are independent processes where failure isolation is valuable.

The principal communication mechanisms are:

- typed D-Bus interfaces for system and session services;
- standard desktop portals for sandboxed applications;
- Wayland protocols for compositor-specific capabilities;
- CXX-Qt only when a Rust model must live directly inside a Qt process.

QML owns presentation and interaction. Rust owns persistent state, validation, policy, and privileged behavior.

### Configuration hierarchy

Official configuration follows:

`Global → Monitor → Workspace → Set → Application`

A more specific layer overrides an earlier layer. Every exposed value retains provenance so the GUI can display, for example:

> Autohide is defined by Set “Work”.

The standard reversal action is **Restore inherited value**, not a context-free reset.

Sets are temporary layers. Leaving a Set restores prior settings unless the user explicitly promotes a change to another scope.

### Persistent state principles

Persistent state is:

- versioned;
- schema-validated;
- migrated explicitly;
- recoverable when a migration fails;
- separated from caches and derived indexes;
- inspectable through official tools.

No application should need to parse another component’s private storage. Cross-component state flows through defined interfaces.

## 3. Package and transaction architecture

Felunyx presents multiple package ecosystems through one planning experience while preserving their differences.

### Source priority

Default resolution order:

1. Felunyx repository
2. Arch official repositories
3. curated AUR catalog
4. Flatpak when sandboxing or upstream distribution makes it the better source
5. Nix for unavailable, versioned, isolated, or development-oriented needs
6. unmanaged/manual sources only through explicit user action

The user can override a recommendation. The system shows the selected source and the reason for the default.

### Transaction pipeline

A system-changing request follows:

1. normalize the request;
2. resolve source candidates;
3. calculate dependencies and conflicts;
4. classify risk;
5. decide snapshot scope;
6. present an exact proposal;
7. request confirmation;
8. execute source-specific stages in a controlled order;
9. verify results;
10. record action history;
11. set reboot-pending state when required.

Full system updates always require confirmation in the GUI. The CLI requires an explicit non-interactive flag such as `--assume-yes`.

### Risk model

Risk is classified as low, moderate, or high using:

- a curated list of critical packages;
- dependency and reverse-dependency impact;
- kernel, bootloader, driver, desktop, filesystem, package-manager, and authentication rules;
- transaction size and replacement patterns;
- source trust and catalog freshness;
- known blocked versions.

Snapshot policy is configurable:

- **Smart** — default; snapshot high-risk operations and selected moderate-risk operations;
- **Always** — snapshot eligible system transactions;
- **Never** — no automatic snapshots, with a clear warning.

The default behavior avoids snapshots for routine low-risk changes.

## 4. Desktop experiences

### Official profiles

One graphical profile is selected during installation:

1. KDE Plasma — primary reference experience
2. XFCE — lightweight, traditional experience
3. Hyprland — modern, advanced experience
4. Felunyx Desktop — only offered when mature enough for its declared channel

Installing one profile avoids default conflicts. Additional profiles may later be installed intentionally through documented tooling.

All profiles share:

- Felunyx visual tokens;
- Central and Settings;
- package and update services;
- Sets and rules;
- recovery;
- session concepts;
- common wallpapers, fonts, icons, and sounds;
- platform APIs.

### Native Felunyx Desktop

The native desktop is:

- Wayland-only as an official session;
- XWayland-compatible for legacy applications;
- Rust-first in compositor and policy code;
- derived from a mature Wayland compositor foundation rather than rebuilding low-level compositor infrastructure unnecessarily;
- expected to preserve the Rust + Smithay technology lineage when the prototype validates it;
- rendered and presented through Qt 6/QML for shell and graphical applications;
- divided into compositor, shell, settings, Central, greeter, and platform services.

The preferred first Phase 8 prototype foundation is `pop-os/cosmic-comp`. That preference is provisional: Felunyx does not adopt the COSMIC desktop, shell, configuration model, or private services merely because the compositor currently depends on them. The prototype must prove that the useful low-level compositor foundation can be separated from unnecessary COSMIC-specific policy while retaining a sustainable upstream synchronization path.

Compositor ownership is split conceptually into two zones:

- **upstream-derived foundation** — hardware discovery, DRM/KMS, render/input plumbing, standard Wayland protocol implementation, XWayland lifecycle, output plumbing, presentation infrastructure, and generic compatibility work should stay close to the mature upstream foundation where sustainable;
- **Felunyx compositor policy** — workspace identity and lifecycle, Floating/Snap/Tiling/Rolling/Monocle, transversal stacks, focus and placement policy, deterministic transitions, rules, Work Environment integration, compositor-owned restoration, and semantic shell state are Felunyx responsibilities.

Generic fixes in the upstream-derived zone should be proposed upstream where practical. Felunyx must not create unrelated rewrites in that zone merely to make the fork appear independent. The size and location of the Felunyx delta must remain measurable.

The compositor continues functioning if the shell restarts. Central and Settings are separate applications. Privileged operations do not run inside QML.

### Window organization

Each workspace has exactly one primary organization mode:

- Floating
- Snap
- Tiling
- Rolling
- Monocle

Stacking is transversal and can exist inside any primary mode.

A mode switch previews the whole workspace and requires explicit application. Primary modes are not mixed inside one workspace.

### Workspaces and monitors

Workspaces are dynamic per monitor. Each monitor has its own ordering and active workspace. One empty trailing workspace is always available.

A named workspace is not automatically pinned. Pinning is explicit.

Disconnected-monitor workspaces move temporarily to the primary monitor while retaining source-monitor identity. On reconnection, Felunyx asks before restoring them unless an automatic policy was configured for that monitor.

## 5. Shell and graphical applications

Qt 6/QML provides:

- panel/taskbar;
- launcher;
- overview;
- notification center;
- quick controls;
- calendar;
- greeter surfaces where appropriate;
- Felunyx Central;
- Felunyx Settings;
- recovery UI when the recovery environment supports Qt.

A shared `Felunyx.UI` design module will define typography, density, motion, surfaces, icons, controls, focus states, accessibility, and visual tokens.

The launcher is a Felunyx personal panel, not a Windows Start menu clone. Familiar taskbar ergonomics do not justify copying Windows layout or hierarchy.

## 6. Sessions, Sets, and rules

### Rules

Ordinary application rules organize applications after they are started. They may select monitor, workspace, mode, stack, position, initial size, and focus policy.

An approved rule may create its destination workspace. Rules do not launch applications.

### Sets

Sets may:

- create or restore workspaces;
- launch applications;
- restore documents, projects, tabs, and terminal sessions when supported;
- apply layout, appearance, audio, notification, focus, network, Bluetooth, energy, performance, and service preferences;
- reuse already-open applications where possible;
- provide temporary rules.

Set activation shows a preview. Exiting a Set restores temporary configuration but does not close documents or terminate applications without confirmation.

### Restoration fidelity

Restoration attempts, in order:

1. application-native session restoration;
2. Felunyx session protocol integration;
3. window-level reopen and placement;
4. explicit non-restorable status.

Sensitive applications, private browsing windows, password managers, and banking contexts are excluded by default.

## 7. Recovery architecture

Recovery is a supported product surface, not a terminal shortcut.

Categories:

- Boot
- System
- Storage
- Packages
- Diagnostics

Every recovery tool follows:

`Analysis → Proposal → Confirmation → Result`

The proposal displays exact commands, files, mounts, packages, and effects. A full terminal remains available.

The recovery environment supports networking but does not enable remote access or submit reports without consent. Known networks may reconnect; new networks request credentials.

## 8. Failure containment

- compositor and shell are separate;
- Central and Settings cannot crash the compositor;
- transaction execution is journaled;
- interrupted transactions have explicit detection and recovery;
- platform services validate schemas before replacing persistent state;
- critical configuration writes use atomic replacement;
- network-dependent operations fail without making offline recovery unavailable;
- snapshot metadata is retained until the associated boot/update is considered stable;
- XWayland starts on demand;
- desktop profile adapters cannot bypass platform safety policy.

## 9. Delivery infrastructure

Later phases will add:

- reproducible ISO definitions;
- signed Felunyx package repositories;
- CI for package builds, ISO builds, linting, unit tests, integration tests, and boot smoke tests;
- curated AUR build and verification infrastructure;
- stable, testing, and development channels only when each has an operational purpose;
- artifact provenance and checksums;
- mirror health and fallback;
- release criteria and rollback procedures.

No release channel exists merely because its name sounds mature.

## 10. Repository shape

The repository starts documentation-first. Implementation directories are added with the phase that owns them.

Target top-level responsibilities:

- `docs/` — product, architecture, governance, plans, and status
- `iso/` — image definition and installer integration
- `packages/` — Felunyx package recipes and repository metadata
- `profiles/` — KDE, XFCE, and Hyprland integration
- `platform/` — Rust services and shared domain models
- `desktop/` — native Felunyx Desktop components
- `tools/` — build, validation, release, and developer utilities
- `tests/` — cross-component and image-level tests

Boundaries are split by responsibility, not by programming language.

## 11. Architectural invariants

The following must remain true unless superseded by an accepted architecture decision:

- official functionality has a graphical path;
- GUI and CLI use the same backend;
- QML does not own privileged policy;
- package sources remain identifiable;
- high-risk operations are never hidden inside unrelated actions;
- recovery proposals are inspectable;
- one workspace has one primary organization mode;
- stacking remains transversal;
- rules organize; Sets may launch;
- desktop profiles share the platform;
- the native desktop does not block the distribution’s first usable releases;
- mature upstream compositor infrastructure is reused where that reduces maintenance without surrendering Felunyx-owned desktop policy;
- user data is preserved by default during system restoration.
