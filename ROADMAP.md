# Felunyx OS Roadmap

Felunyx is developed through review-gated phases. A phase is complete only when its exit criteria are met and the result is reviewed. Starting the next phase is a deliberate decision.

The roadmap describes order and proof, not release dates.

## Validation gates

Every phase declares evidence through three possible gates:

- **R — Remote:** source, schemas, documentation, static analysis, unit/contract tests, manifests, and CI artifacts.
- **V — Virtual:** boot, installation, reboot, recovery, and integration exercised in disposable virtual machines.
- **H — Hardware:** physical firmware, graphics, radios, peripherals, power management, storage, displays, and long-running behavior.

A phase requires only the gates relevant to its promise. Passing R never implies V or H. Work blocked solely by V or H may allow isolated preparation for the next phase, but neither phase is marked complete until its required evidence passes. See [the validation-gates policy](docs/process/validation-gates.md).

## Phase 1 — Foundation and architecture

**Goal:** establish one canonical understanding of what Felunyx is and how it will be built.

### Deliverables

- vision and philosophy;
- system architecture;
- accepted decision register;
- product specifications for desktop, packages, recovery, sessions, and installer;
- repository and contribution model;
- phased implementation roadmap;
- security posture;
- written foundation design specification.

### Exit criteria

- no placeholder requirements;
- no contradictions between canonical documents;
- every major accepted conversation decision is represented;
- deferred decisions have explicit triggers;
- repository links and Markdown structure validate;
- foundation changes are available in a reviewable pull request;
- the user approves the written specification.

**Current state:** complete and approved.

---

## Phase 2 — Reproducible ISO skeleton

**Goal:** produce a minimal, repeatable, bootable Felunyx image without pretending the full experience exists.

### Scope

- image build tooling;
- pinned build environment;
- package manifest;
- Felunyx repository bootstrap;
- Linux Zen and Linux LTS;
- systemd boot path;
- Btrfs automatic-layout prototype;
- GRUB as the only installed and validated Phase 2 bootloader path; Limine remains isolated research;
- minimal Calamares integration;
- KDE-only internal profile;
- virtual-machine boot tests;
- artifact checksums and build metadata.

### Exit criteria

- two clean builds from the same input produce equivalent package manifests and configuration payloads;
- ISO boots in supported test VMs;
- live session starts;
- Calamares can install the internal KDE profile to a disposable VM;
- installed system reboots through GRUB;
- Linux LTS fallback is visible and bootable;
- build and smoke-test commands are documented;
- failures produce retained logs and artifacts.

---

## Phase 3 — Core platform and safe transactions

**Goal:** establish the backend shared by every Felunyx experience.

### Scope

- Rust workspace and service boundaries;
- typed configuration schema and inheritance;
- action journal;
- package source catalog;
- transaction planner;
- pacman backend;
- risk classification;
- snapshot orchestration;
- reboot-pending state;
- system health model;
- initial CLI using the shared backend;
- D-Bus contracts;
- unit and integration test harness.

### Exit criteria

- GUI-independent tests prove planning, risk, confirmation, execution, and journal behavior;
- high-risk simulated transactions select the intended snapshot scope;
- interrupted transaction fixtures recover to a defined state;
- configuration provenance and inherited reset are testable;
- the CLI cannot bypass confirmation without an explicit flag;
- no package source is represented without source identity.

---

## Phase 4 — KDE reference experience

**Goal:** make Felunyx recognizable and comfortable on its first production-oriented desktop.

### Scope

- Felunyx design tokens;
- KDE theme and layout;
- panel/taskbar behavior achievable through supported integration;
- Felunyx launcher strategy for the KDE phase;
- Settings and Central shells in Qt/QML;
- notification, quick-control, calendar, and session integration;
- wallpapers, fonts, icons, sounds, and accessibility;
- default application selection;
- onboarding;
- Sets and rules first usable workflows.

### Exit criteria

- ordinary official configuration is possible through GUIs;
- visual states cover loading, empty, error, confirmation, and success;
- KDE updates do not require fragile undocumented patches;
- accessibility and keyboard navigation pass the phase checklist;
- the experience remains usable without blur or animation;
- launcher familiarity does not become Windows imitation;
- user testing confirms the system feels authored rather than themed.

---

## Phase 5 — Installer, recovery, security, and hardware readiness

**Goal:** turn the internal image into a system that can be responsibly installed and recovered.

### Scope

- complete Calamares flow;
- automatic and manual partitioning;
- encryption;
- dual-boot handling;
- bootloader selection;
- driver and firmware handling;
- recovery environment;
- snapshot browser and restore workflow;
- NVIDIA, AMD, Intel, hybrid graphics, audio, Bluetooth, tablet, printing, gamepad, suspend, and hibernation policy;
- firewall;
- Secure Boot prototype;
- diagnostic export with consent.

### Exit criteria

- destructive installer actions have explicit summaries;
- failed installations retain actionable logs;
- supported hardware matrix is published;
- recovery can boot LTS, inspect snapshots, repair packages, and rebuild boot artifacts;
- system restore preserves home by default;
- home restore creates a safety snapshot;
- remote access and report submission remain off without consent;
- Secure Boot is either verified end-to-end or clearly not advertised.

---

## Phase 6 — XFCE and Hyprland parity

**Goal:** add distinct official profiles without fragmenting the platform.

### Scope

- XFCE lightweight profile;
- Hyprland advanced profile;
- adapters for Sets, rules, notifications, settings provenance, and recovery;
- profile-specific defaults;
- cross-profile visual tokens;
- profile switching and installation policy;
- performance and accessibility validation.

### Exit criteria

- each profile uses the same platform backend;
- each profile has documented capability differences;
- no profile silently bypasses safety or package policy;
- profile-specific configuration does not corrupt another profile;
- installation still selects only one graphical profile by default;
- common workflows use consistent terminology.

---

## Phase 7 — Distribution infrastructure and private alpha

**Goal:** operate Felunyx as a maintained distribution rather than a local image.

### Scope

- signed package repositories;
- build workers;
- curated AUR pipeline;
- metadata freshness and version blocking;
- mirror strategy;
- release channels justified by operations;
- update rollout and rollback;
- issue triage;
- private alpha documentation;
- privacy-preserving diagnostics;
- release engineering runbooks.

### Exit criteria

- packages and repository metadata are signed and validated;
- a compromised or failed package version can be blocked;
- repository outage has documented fallback behavior;
- alpha testers can install, update, report, and recover;
- update rollouts can pause without rebuilding the entire distribution;
- operating costs and maintenance duties are understood.

---

## Phase 8 — Native Felunyx Desktop prototype

**Goal:** validate the architectural bets behind the future desktop while proving that a mature compositor foundation can be adapted sustainably.

This is a parallel research and implementation track that may begin experimentally earlier, but it does not become an official install profile before this gate.

`pop-os/cosmic-comp` is the preferred first prototype foundation because it preserves the Rust + Smithay lineage while already providing mature compositor infrastructure. This preference is provisional: the phase must prove that Felunyx can separate useful low-level infrastructure from unnecessary COSMIC-specific policy and services without creating an unsustainable fork.

### Scope

- pin and build a known-good mature compositor baseline, beginning with `cosmic-comp`;
- nested and TTY launch;
- establish a repeatable upstream synchronization baseline before large Felunyx changes;
- inventory COSMIC-specific configuration, protocol, settings-daemon, shell, presentation-library, workspace, output, input, and accessibility coupling;
- replace or bridge only enough COSMIC-specific integration to start a minimal Felunyx Qt/QML shell;
- prove shell restart without compositor-managed application loss;
- multi-monitor hotplug;
- fractional scaling;
- XWayland on demand;
- portals and screen sharing;
- input methods;
- tablet input;
- Floating plus at least one clearly Felunyx-specific nontrivial workspace behavior as a vertical slice;
- Tiling, Rolling, and stack architecture validation;
- deterministic compositor-state serialization and restoration;
- classify the Felunyx patch delta as upstream-retained, adaptation boundary, Felunyx policy, or upstream candidate;
- integrate a newer upstream revision and measure synchronization cost;
- Settings integration.

### Exit criteria

- the prototype passes the declared hardware and protocol matrix;
- shell crashes do not destroy compositor state or terminate compositor-managed applications;
- the Felunyx Qt/QML shell can operate without adopting the COSMIC shell architecture;
- COSMIC-specific dependencies have explicit keep/replace/remove rationale and do not silently become Felunyx public contracts;
- Felunyx-owned workspace, layout, stack, focus, rule, Work Environment, and restoration policy can remain structurally separated from low-level upstream-derived backend plumbing;
- window-mode transitions and restoration have deterministic tests;
- performance is measured rather than assumed;
- the size and location of the Felunyx patch delta are documented;
- at least one newer upstream compositor revision is integrated during the prototype so merge/rebase burden is measured rather than guessed;
- inherited license and attribution obligations are documented;
- the project explicitly decides whether `cosmic-comp` becomes the accepted long-term foundation, another mature compositor foundation is evaluated, or the desktop remains research;
- no result is promoted beyond the strongest R/V/H evidence actually achieved.

---

## Phase 9 — Public beta

**Goal:** validate Felunyx with a wider audience while preserving honest support boundaries.

### Scope

- public ISO and signatures;
- upgrade policy;
- beta release notes;
- known-issues registry;
- documentation from installation through advanced use;
- support and triage workflow;
- migration tests;
- failure-rate and recovery-success review;
- accessibility and localization baseline.

### Exit criteria

- installation, update, rollback, and recovery are documented and repeatedly exercised;
- supported hardware and unsupported cases are explicit;
- no critical data-loss issue remains open;
- package repository operations have on-call ownership;
- beta-to-beta upgrades are tested;
- feedback shows the product identity survives outside the original design context.

---

## Phase 10 — Stable 1.0

**Goal:** declare only the capabilities the project can maintain.

### Exit criteria

- stable support policy exists;
- critical security update path is proven;
- release artifacts are reproducible enough for independent verification of manifests and payloads;
- recovery documentation matches the shipped environment;
- package and ISO signing keys have documented rotation and revocation;
- upgrade compatibility commitments are written;
- the project can sustain maintenance after launch;
- every advertised feature is present, tested, and documented.

## Cross-phase rules

- No phase is skipped because a later feature is more exciting.
- Experimental work may occur in parallel but cannot redefine accepted interfaces without updating the specification.
- A feature is not complete without failure handling, tests, and documentation.
- Native desktop work never blocks the first useful Felunyx distribution.
- Phase boundaries are review points, not ceremonial labels.
- Completion claims name the strongest gate actually passed: R, V, or H.
- A hardware-blocked phase may allow isolated next-phase preparation, but blocked evidence is never waived or disguised as success.
