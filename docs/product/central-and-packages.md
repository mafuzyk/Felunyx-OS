# Felunyx Central and Package Management

## Product separation

Felunyx Central is an authored system dashboard. Felunyx Settings configures behavior. The package engine performs transactions. These are related but not interchangeable.

Central must not become a clone of KDE System Settings or a storefront that hides package reality.

## Central home

Initial areas:

- System Health
- Updates
- Applications
- Recent Actions
- Recovery

The home page emphasizes state and required decisions rather than promotional content.

## Shared backend

The GUI and CLI consume the same Rust services and domain models.

Both expose:

- requested action;
- selected source;
- candidate version;
- dependencies;
- conflicts;
- packages added, removed, replaced, or rebuilt;
- download and build sizes;
- trust and verification status;
- risk classification;
- snapshot decision;
- restart or reboot requirement;
- execution stages;
- result and recovery path.

The GUI may summarize, but exact details remain available before confirmation.

## Source policy

Default priority:

1. Felunyx repository
2. Arch official repositories
3. curated AUR
4. Flatpak
5. Nix
6. unmanaged/manual source

This is a policy, not a claim that every package should come from the first available source.

### Felunyx repository

Contains:

- native Felunyx components;
- necessary integration packages;
- upstream packages patched only for justified compatibility or experience;
- curated prebuilt community packages where maintenance and trust justify it.

Every fork or patch set documents:

- reason;
- delta;
- tests;
- security and update ownership;
- upstream plan;
- removal condition.

### Arch repositories

Preferred for ordinary system packages when no Felunyx-specific integration is required.

### Curated AUR

AUR packages enter a managed catalog through automated inspection, build, verification, and signing.

The client validates:

- catalog freshness;
- package version;
- source metadata;
- hashes;
- Felunyx build signature;
- blocked-version status.

Human review is reserved for suspicious or high-impact cases rather than every routine rebuild.

A package that fails verification is blocked at that version in the managed layer. The user may still use standard Arch tooling manually, but Central marks the result unmanaged.

### Flatpak

Preferred when:

- upstream Flatpak maintenance is stronger;
- sandboxing materially improves safety;
- the application is naturally self-contained;
- system integration remains acceptable.

Permissions are visible and configurable through Felunyx Settings.

### Nix

Used for:

- unavailable packages;
- multiple or pinned versions;
- isolated development environments;
- reproducible toolchains;
- software whose dependency model is better served by Nix.

Nix does not replace pacman as the operating-system base.

## Source selection

Central recommends one source and explains the reason.

The user may inspect alternatives and override the recommendation. Overrides remain specific unless the user creates a persistent policy.

Source selection never merges distinct package identities without evidence.

## Transaction model

### Plan

Before changing the system, the engine produces an immutable plan containing:

- request;
- source stages;
- dependency graph summary;
- file or package conflicts;
- risk level and reasons;
- snapshot scope;
- expected service restarts;
- reboot requirement;
- estimated space effects.

### Confirmation

Full system updates always require confirmation.

Routine application actions may use a concise confirmation policy, but destructive, source-changing, privilege-changing, or high-risk actions always show an explicit proposal.

Non-interactive CLI execution requires an explicit flag.

### Execution

Source-specific operations run in a controlled sequence. A common transaction does not imply one giant atomic operation across incompatible package ecosystems.

The journal records stage boundaries so that a failure can say:

- what completed;
- what did not begin;
- what failed;
- whether rollback is available;
- what manual state remains.

### Verification

After execution, the engine validates:

- package database state;
- expected versions;
- service or boot metadata updates;
- snapshot metadata;
- action journal;
- reboot-pending reason.

## Risk classification

### Low

Examples:

- isolated application update;
- no critical dependencies;
- no boot, driver, authentication, storage, or desktop-core changes.

Default: no automatic snapshot in Smart mode.

### Moderate

Examples:

- larger dependency replacement;
- desktop component updates;
- service changes with limited system impact;
- AUR rebuild with broad reverse dependencies.

Default: snapshot only when a specific rule or impact threshold applies. The user can manually request one.

### High

Examples:

- kernel;
- bootloader;
- initramfs tooling;
- graphics driver;
- filesystem tooling;
- authentication;
- package manager;
- snapshot tooling;
- broad core-system replacement;
- known risky migration.

Default: automatic snapshot in Smart mode.

Risk is explained using concrete reasons, not a mysterious score.

## Snapshot options

- Smart — recommended
- Always
- Never

“Never” remains available because control matters, but the interface explains the lost recovery path before accepting it.

## Reboot-pending state

When an update changes a kernel, driver, desktop core, central platform component, or other reboot-sensitive element, Felunyx shows:

- why a reboot is required;
- which transaction caused it;
- whether an associated snapshot is retained;
- whether the system has booted successfully into the new state.

The snapshot remains protected until stability criteria are met.

## Failure behavior

### Network failure

- preserve the plan;
- retain downloaded verified artifacts;
- do not pretend a partial source refresh is current;
- offer retry;
- keep offline recovery available.

### Mirror inconsistency

- identify repository and metadata age;
- retry a healthy mirror when policy allows;
- never disable signature validation to “make it work.”

### AUR build failure

- show build stage and logs;
- do not mark the package updated;
- continue unrelated stages only when the plan declared them independent;
- preserve the prior installed package where possible.

### Interrupted transaction

- detect journal state on next start;
- analyze package database and stage markers;
- propose completion, rollback, or manual recovery;
- never hide the interruption behind a generic failure banner.

## Initial CLI

The command name `fel` is provisional.

Conceptual command families:

- `fel status`
- `fel search`
- `fel install`
- `fel remove`
- `fel update`
- `fel plan`
- `fel history`
- `fel rollback`
- `fel source`
- `fel doctor`

Names and exact options freeze only after the Phase 3 interface specification and tests exist.
