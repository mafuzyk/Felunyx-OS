# Felunyx OS Foundation Design

**Date:** 2026-08-03

**Status:** Written and self-reviewed; awaiting user review

**Scope:** Product constitution, architecture, repository model, and phased delivery strategy

## 1. Goal

Define Felunyx precisely enough that future implementation can be decomposed into testable phase plans without repeatedly reopening foundational identity and architecture questions.

Phase 1 produces documentation and governance. It does not produce an ISO, package manager, desktop environment, or promise of a release date.

## 2. Context

Felunyx is the successor to earlier distribution experiments and retains their strongest intent: a Linux system that is fast, comfortable, visually authored, customizable, safe to change, and honest about how it works.

The project has already selected major directions through collaborative design:

- Arch Linux base;
- systemd;
- rolling release;
- Btrfs recovery model;
- KDE first, XFCE and Hyprland later;
- native Wayland desktop in Rust + Smithay with Qt/QML interfaces;
- shared platform services;
- unified but source-honest package experience;
- GUI-first official functionality;
- taskbar, launcher, workspace, Set, rule, and recovery concepts;
- explicit phase boundaries.

The repository was initialized publicly under `mafuzyk/Felunyx-OS` with GPLv3.

## 3. Approaches considered

### Approach A — Build the native desktop first

Advantages:

- strongest immediate identity;
- fewer compromises from adapting existing desktops;
- direct path to the intended window model.

Costs:

- delays the first usable distribution;
- couples ISO, package platform, recovery, and desktop risk;
- expands protocol, rendering, hardware, accessibility, and shell scope before distribution infrastructure exists.

**Decision:** rejected as the critical path. Native desktop work remains a parallel gated track.

### Approach B — Ship an Arch profile collection

Advantages:

- quick ISO;
- low initial engineering cost;
- easy use of existing desktop tooling.

Costs:

- risks becoming theming plus package selection;
- duplicates behavior across KDE, XFCE, and Hyprland;
- leaves updates, recovery, Sets, rules, and settings fragmented;
- weakens Felunyx identity.

**Decision:** rejected as the product architecture.

### Approach C — Phased distribution platform with a reference desktop

Advantages:

- produces a useful system before the native desktop;
- centralizes package, recovery, configuration, session, and rule behavior;
- lets KDE validate the platform;
- allows XFCE, Hyprland, and the future desktop to consume shared contracts;
- separates delivery risk from desktop research risk.

Costs:

- requires careful adapters;
- some first-version interactions cannot fully match the native design;
- demands discipline to avoid permanent KDE-specific assumptions.

**Decision:** accepted and recommended.

## 4. Product identity

Felunyx is a visually authored, technically transparent Arch-based distribution.

Canonical phrase:

> Beauty must arise from architecture, not be pasted over.

Visual direction:

- graphite base;
- blue/violet accents;
- technical, clean, delicate;
- restrained ethereal edge;
- frosted rather than clear glass;
- compact default density;
- no neon-gamer identity;
- no excessive cute styling;
- no direct commercial-desktop imitation.

The lynx symbol balances geometry and expression.

## 5. System foundation

### Base

- Arch Linux directly;
- rolling release;
- systemd;
- Felunyx repository before Arch repositories;
- selective package ownership.

### Boot and kernel

- Linux Zen default;
- Linux LTS fallback;
- GRUB recommended;
- Limine official alternative;
- one installed bootloader.

### Storage

- Btrfs;
- separated system and home scopes;
- high-risk transaction snapshots;
- system restore preserves home;
- home restore first protects current home.

### Installer

One customized Calamares ISO. One graphical profile selected during installation.

The first internal implementation includes KDE only. That is a sequencing decision, not a product cancellation of XFCE or Hyprland.

## 6. Platform architecture

Desktop-independent Rust services own:

- package sources;
- transaction planning and execution;
- risk analysis;
- snapshots;
- reboot state;
- system health;
- configuration inheritance;
- sessions;
- Sets;
- rules;
- action history;
- recovery metadata.

GUI and CLI use the same services.

Configuration hierarchy:

`Global → Monitor → Workspace → Set → Application`

Persistent values preserve provenance.

## 7. Packages and updates

Default source policy:

`Felunyx → Arch → curated AUR → Flatpak → Nix`

Source override is supported and explained.

Transactions expose exact package and source effects. High-risk changes create snapshots in Smart mode. Full system updates require confirmation. The CLI needs an explicit non-interactive confirmation flag.

AUR integration uses a curated, built, verified, signed, freshness-aware managed layer. Manual Arch behavior remains possible but is identified as unmanaged.

## 8. Desktop strategy

### Profiles

- KDE Plasma: reference and first implementation
- XFCE: official lightweight profile
- Hyprland: official advanced profile
- Felunyx Desktop: native future profile when mature

All consume one platform.

### Native desktop

- Wayland-only official session;
- XWayland on demand;
- Rust + Smithay compositor;
- Qt 6/QML shell and graphical applications;
- QML presentation, Rust policy;
- separate compositor and shell failure domains;
- D-Bus services, portals, and compositor-specific Wayland protocols.

Smithay remains an accepted decision, but the prototype gate can force reconsideration if evidence contradicts the assumptions.

## 9. Desktop interaction

### Window modes

One primary mode per workspace:

- Floating
- Snap
- Tiling
- Rolling
- Monocle

Stacking is transversal.

Mode transitions preview the entire workspace and require Apply. Focus changes do not resize Smart Tiling. Rolling direction adapts to monitor orientation.

### Workspaces

Dynamic per monitor, one trailing empty workspace, naming separate from pinning, abstract overview diagrams, and temporary source-monitor groups after disconnect.

### Launcher

Traditional, compact, and quickly understandable, but explicitly not Windows-like.

Home includes Fixed and Recent applications. Search includes files and actions without putting files into the default home. All applications is a separate view.

### Settings

The GUI is the primary complete interface, with:

- search;
- common controls visible;
- advanced controls collapsed;
- scope selection;
- provenance;
- preview;
- Apply/Cancel for consequential changes;
- keyboard navigation;
- shortcut remapping;
- declarative export/import.

## 10. Rules, Sets, and restoration

Rules organize after launch. Sets may launch.

An approved rule may create a missing workspace. A Set previews application, layout, device, and configuration effects.

A Set previews its effects and reuses already-open applications where possible.
By default, activation preserves the current arrangement and creates or reuses additional Set workspaces; replacing the current arrangement is an explicit preview choice.

Restoration attempts exact documents, projects, tabs, URLs, and terminal sessions using application-native support first. Sensitive contexts are excluded by default.

## 11. Recovery

Recovery is categorized into Boot, System, Storage, Packages, and Diagnostics.

Every action follows:

`Analysis → Proposal → Confirmation → Result`

Exact commands and affected state are visible. Network is available without enabling remote access or automatic reporting. A full terminal exists.

Boot failure asks instead of silently choosing.

## 12. Repository model

Felunyx begins as a phased monorepo.

This repository owns:

- canonical documentation;
- ISO and installer definitions;
- package recipes and integration;
- shared platform services;
- desktop profiles;
- early native desktop work;
- cross-component tests and tools.

A split requires independent cadence, access, ownership, size, CI, or upstream-collaboration justification.

## 13. Delivery phases

1. Foundation and architecture
2. Reproducible ISO skeleton
3. Core platform and safe transactions
4. KDE reference experience
5. Installer, recovery, security, and hardware
6. XFCE and Hyprland parity
7. Distribution infrastructure and private alpha
8. Native desktop prototype
9. Public beta
10. Stable 1.0

Implementation stops at each boundary for review.

## 14. Error handling principles

- failures retain evidence;
- interrupted operations are journaled;
- source-specific package failures remain identifiable;
- network failures do not remove offline recovery;
- shell failure does not terminate the compositor;
- UI failure does not run privileged fallback logic;
- critical writes are atomic;
- configuration migrations validate before replacement;
- recovery never claims “no change” without verification.

## 15. Testing strategy

Each owning phase adds tests at the lowest responsible layer.

Required categories over the roadmap:

- schema and unit tests;
- D-Bus/contract tests;
- package planner and risk fixtures;
- snapshot and restore tests;
- interrupted transaction tests;
- VM boot tests;
- installer tests;
- fallback kernel tests;
- desktop adapter tests;
- Wayland protocol and compositor-state tests;
- accessibility review;
- reduced-motion and no-blur visual checks;
- hardware matrix;
- upgrade and migration tests;
- signed repository and blocked-version tests;
- recovery failure injection.

A feature is not complete with happy-path manual verification alone.

## 16. Security and privacy

- no default telemetry;
- no remote access by default;
- explicit diagnostic preview and consent;
- signed package and repository metadata;
- visible package source and trust;
- firewall enabled provisionally;
- encryption prominently recommended;
- Secure Boot advertised only after end-to-end verification;
- sensitive session contexts excluded by default.

## 17. Non-goals for Phase 1

Phase 1 does not:

- create production code;
- freeze component API names;
- choose exact Btrfs subvolume names;
- select every default application;
- claim Secure Boot support;
- publish an ISO;
- promise a schedule;
- begin Phase 2 without user review.

## 18. Acceptance criteria

Phase 1 is ready for user review when:

- canonical documents exist;
- approved decisions are represented;
- contradictions are resolved;
- provisional choices are marked;
- deferred choices have triggers;
- Markdown links resolve;
- placeholder scans pass;
- a reviewable branch and draft PR exist.

Phase 1 completes only after the user approves the written specification.
