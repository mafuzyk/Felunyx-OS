# Native compositor foundation design

**Date:** 2026-08-09  
**Status:** proposed architecture update for review  
**Active project phase:** Phase 2 — Reproducible ISO Skeleton  
**Implementation phase owned by:** Phase 8 — Native Felunyx Desktop prototype

## Purpose

Felunyx needs a native compositor because its desktop model includes behaviors that are difficult to maintain as superficial extensions over unrelated desktop environments: per-workspace organization modes, transversal stacks, monitor-local dynamic workspaces, deterministic restoration, and deep integration with Work Environments.

That requirement does **not** imply that Felunyx should rebuild the mature low-level foundations of a Wayland compositor from bare Smithay building blocks.

This design changes the implementation strategy from **“build the compositor directly on Smithay”** to **“derive the compositor from a mature Wayland compositor foundation and spend Felunyx engineering effort on Felunyx-owned policy.”**

The preferred first foundation for the Phase 8 prototype is `pop-os/cosmic-comp`.

This is not a decision to ship the COSMIC desktop, reuse the COSMIC shell, or copy COSMIC product behavior. It is a decision to begin from a working Rust/Smithay compositor and evaluate how much of its low-level implementation can remain upstream-derived while Felunyx replaces desktop policy and presentation.

## Why this changes the previous direction

Phase 1 accepted Rust + Smithay because it fits the desired language, safety, process boundaries, and Wayland-native architecture. That decision correctly chose a technology family but assumed Felunyx should assemble the compositor starting near the Smithay layer itself.

Further review identified a maintenance problem with that assumption. Smithay deliberately provides compositor building blocks rather than a finished compositor. Reimplementing mature DRM/KMS, renderer selection, input, XWayland lifecycle, output handling, protocol integration, and hardware edge-case behavior would consume large amounts of engineering time before Felunyx reaches the behavior that actually differentiates the project.

Felunyx already has a project principle that favors selective ownership: build what defines the experience and integrate mature upstream work elsewhere. The compositor strategy should follow the same rule.

## Alternatives considered

### A. Bare Smithay compositor

Start from Smithay and implement the compositor skeleton directly.

Advantages:

- maximum architectural control;
- smallest inherited policy surface;
- direct understanding of every compositor subsystem.

Disadvantages:

- recreates large amounts of already-working compositor infrastructure;
- delays user-visible Felunyx behavior behind hardware and protocol work;
- creates the largest testing matrix and maintenance burden for a small project;
- makes hardware compatibility a Felunyx-owned problem earlier than necessary.

**Decision:** no longer the preferred implementation strategy. Smithay remains an important upstream foundation and reference.

### B. Derive from `cosmic-comp`

Begin the prototype from a pinned `cosmic-comp` revision and progressively separate reusable compositor infrastructure from COSMIC-specific policy and dependencies.

Advantages:

- Rust and Smithay match the existing Felunyx direction;
- mature compositor infrastructure already exists;
- the codebase already exercises DRM, GBM, EGL, libinput, udev, multiple renderers, Wayland frontend behavior, X11 backend support, and XWayland;
- the architecture is closer to Felunyx's desired workspace, floating/tiling, and stack concepts than a generic compositor starting point;
- the fork can continue consuming Smithay and upstream compositor fixes if the delta stays controlled;
- GPL-3.0-only is compatible with Felunyx's repository-wide GPL-3.0 direction for a derived compositor component.

Disadvantages:

- `cosmic-comp` currently depends on COSMIC-specific configuration, protocols, settings-daemon configuration, and `libcosmic` components;
- upstream has its own product policy and release priorities;
- a careless fork could diverge until upstream synchronization becomes impractical;
- inherited assumptions must be identified before they become Felunyx contracts.

**Decision:** preferred Phase 8 prototype foundation, subject to the decoupling and maintenance gates below.

### C. KWin, Niri, or another mature compositor foundation

Keep mature alternatives available as comparison and fallback candidates.

KWin is especially valuable as a compatibility and behavior reference because of its long hardware and Wayland history, but a C++/Qt KWin-derived compositor would move the native compositor away from the Rust/Smithay architecture and may require a broader policy rewrite.

Niri is a useful Rust/Smithay reference with a focused compositor architecture, but its scrollable-tiling model is more specialized than the multi-mode workspace policy Felunyx intends to own.

**Decision:** retain as comparative references and fallback candidates. The Phase 8 prototype may change foundation if `cosmic-comp` fails its gates.

## Upstream evidence captured for this design

The preferred prototype source inspected for this decision is:

- repository: `pop-os/cosmic-comp`;
- inspected commit: `d3ffa814941f6294864d5ecdc9796f818ddb1ac8`;
- manifest package version: `1.0.0`;
- Rust edition: `2024`;
- declared license: `GPL-3.0-only`;
- declared minimum Rust version: `1.93`;
- Smithay manifest version: `0.7.0`;
- Smithay git patch at the inspected revision: `cdc03f7`.

The inspected manifest enables Smithay facilities including DRM, GBM, EGL, libinput, libseat sessions, udev, winit, Vulkan, X11, the desktop helpers, multiple renderer paths, the Wayland frontend, and XWayland.

The same manifest also records COSMIC-specific dependencies that must not silently become Felunyx platform contracts, including `cosmic-config`, `cosmic-protocols`, `cosmic-settings-config`, `cosmic-settings-daemon-config`, `iced_*`, and `libcosmic`.

These values are research evidence, **not Felunyx dependency pins**. Phase 8 must refresh upstream state and choose its own locked revisions before implementation.

## Architectural ownership

The derived compositor is divided conceptually into three ownership zones.

### 1. Upstream-derived compositor foundation

Felunyx should avoid unnecessary changes in this zone.

Candidate responsibilities:

- DRM/KMS and device discovery;
- GBM/EGL and renderer plumbing;
- libinput and low-level input plumbing;
- output enumeration and mode setting;
- frame/render scheduling primitives;
- standard Wayland protocol implementation;
- XWayland lifecycle and compatibility plumbing;
- direct scanout and presentation infrastructure;
- cursor and surface plumbing;
- hardware quirks that are not Felunyx product policy.

When a change in this zone is generally useful, upstream contribution is preferred over a Felunyx-only patch.

### 2. Felunyx compositor policy

This is the main reason the native compositor exists and is expected to diverge deliberately.

Felunyx owns:

- stable monitor, workspace, window, and stack identities;
- monitor-local dynamic workspace behavior;
- Floating, Snap, Tiling, Rolling, and Monocle workspace modes;
- transversal stacks and tab semantics;
- deterministic mode transitions and previews;
- focus and placement policy;
- application rules that organize but do not launch;
- compositor-side Work Environment integration;
- session serialization and restoration of compositor-owned state;
- semantic state exposed to the shell and platform;
- Felunyx-specific compositor protocols only where standard protocols cannot express the required behavior.

The policy layer should be kept structurally separate from low-level backend code wherever the inherited architecture permits it.

### 3. Felunyx shell and platform

The COSMIC shell is not the Felunyx shell.

Felunyx continues to use:

- Qt 6/QML for authored graphical presentation;
- Rust for state, validation, policy, and privileged behavior;
- typed D-Bus services for desktop-independent platform contracts;
- standard portals for sandbox integration;
- a separate shell process so a shell crash does not destroy compositor-managed applications.

COSMIC-specific presentation libraries and configuration services are not adopted merely because the compositor currently depends on them.

## Fork sustainability policy

A derived compositor is only an improvement if the fork remains maintainable.

Every inherited or modified area must be classified as one of:

1. **Upstream retained** — consumed with minimal or no Felunyx changes.
2. **Adaptation boundary** — a narrow bridge needed to connect upstream-derived infrastructure to Felunyx services.
3. **Felunyx policy** — intentional product behavior owned by Felunyx.
4. **Upstream candidate** — generic fixes or improvements that should be proposed upstream when practical.

Felunyx must not accumulate unrelated cosmetic, formatting, or architectural rewrites in upstream-retained areas merely to make the fork look independent.

Upstream synchronization must be tested regularly during the prototype instead of postponed until the fork is already deeply divergent.

## Decoupling gate

Before `cosmic-comp` can be accepted as the long-term foundation, the Phase 8 prototype must demonstrate that Felunyx can replace COSMIC-specific policy without also taking ownership of unnecessary COSMIC desktop services.

The prototype must inventory and classify:

- `cosmic-config` usage;
- `cosmic-protocols` usage;
- settings-daemon configuration coupling;
- `libcosmic` and `iced_*` dependencies;
- shell-specific assumptions;
- workspace-model assumptions;
- output and input configuration ownership;
- accessibility integration;
- protocol extensions that are COSMIC-specific versus generally reusable.

A dependency may remain when it solves a real compositor problem and its maintenance cost is justified. The objective is not dependency purity; it is a clean ownership boundary.

## Phase 8 prototype sequence

The future prototype should proceed in this order:

1. pin and build a known-good upstream `cosmic-comp` revision without Felunyx changes;
2. boot it nested and from a TTY on the declared test matrix;
3. establish a repeatable upstream-sync baseline;
4. replace or bridge only enough COSMIC-specific shell/config integration to start a minimal Felunyx Qt/QML shell;
5. prove Wayland and XWayland applications survive shell restart;
6. implement one clearly Felunyx-specific workspace behavior as a vertical slice;
7. measure the patch delta and categorize it by ownership zone;
8. update from the pinned upstream revision to a newer tested revision and measure merge cost;
9. only then decide whether `cosmic-comp` becomes the accepted long-term foundation.

Rolling is a strong candidate for the vertical slice because it exercises workspace policy that is distinct from ordinary floating and tiling. The exact prototype behavior is chosen in the owning implementation plan.

## Acceptance gates

`cosmic-comp` becomes the accepted Felunyx compositor foundation only if the prototype demonstrates all of the following.

### Functional

- nested launch;
- TTY launch;
- Wayland applications;
- XWayland applications;
- shell restart without application loss;
- multi-monitor hotplug;
- fractional scaling;
- input methods;
- tablet/pen input;
- screen capture and screen sharing through supported portals;
- at least Floating plus one Felunyx-specific nontrivial layout path;
- deterministic workspace/stack serialization and restoration.

### Architectural

- Felunyx policy can be separated from upstream-derived backend plumbing;
- the Qt/QML shell does not require adopting the COSMIC shell architecture;
- COSMIC-specific service dependencies have an explicit keep/replace/remove rationale;
- no private upstream implementation detail is accidentally frozen as a Felunyx public API.

### Maintenance

- a newer upstream revision can be integrated during the prototype without an unreasonable rebase/merge burden;
- the size and location of Felunyx's delta are measurable;
- generic fixes have a plausible upstream path;
- inherited license and attribution obligations are documented;
- upstream abandonment would leave a survivable maintenance path.

### Validation

The prototype must name the strongest achieved evidence level:

- **R:** source audit, dependency inventory, architecture tests, build/test automation;
- **V:** nested/VM compositor, application, shell-restart, portal, and multi-output scenarios;
- **H:** real GPU, monitor, input, tablet, power, and long-running behavior.

No architecture is accepted solely because it compiles.

## Failure / fallback decision

If the prototype shows that `cosmic-comp` is too tightly coupled to COSMIC services, requires a large invasive delta in low-level code, or cannot be synchronized with upstream at a sustainable cost, Felunyx must stop and compare alternatives rather than forcing the fork through.

Fallback research order is not a permanent ranking, but current candidates are:

1. another Rust/Smithay compositor foundation such as Niri where architectural fit can be proven;
2. KWin-derived architecture if its mature compatibility outweighs language and policy costs;
3. a smaller Smithay-native compositor foundation;
4. bare Smithay only if evidence shows the required behavior cannot be achieved sustainably through a mature base.

Changing foundation after this gate is an architecture decision, not a failed promise.

## Phase boundary

This document changes long-term architecture direction only.

It does **not**:

- begin Phase 8 implementation;
- add `cosmic-comp`, Smithay, KWin, Niri, Qt, or Rust dependencies to the current ISO;
- change the Phase 2 boot, installer, kernel, or validation work;
- authorize a desktop fork today;
- define final compositor APIs, Rust crates, D-Bus interfaces, database schemas, or protocol names.

Phase 2 remains the active phase. Native compositor implementation remains outside the first usable release critical path.

## Decision-register migration

The canonical decision update proposed by this design is:

- mark D-020 as **Superseded** rather than deleting it;
- add an accepted decision that the native compositor will derive from a mature Wayland compositor foundation rather than rebuilding low-level compositor infrastructure unnecessarily;
- add a provisional decision naming `cosmic-comp` as the preferred first Phase 8 foundation, conditional on decoupling, compatibility, and upstream-sync gates;
- preserve Rust + Smithay as the preferred technology lineage while allowing evidence from the prototype to change the exact foundation.

This preserves the original intent while removing the unnecessary assumption that Felunyx must build the floor before it can design the house.
