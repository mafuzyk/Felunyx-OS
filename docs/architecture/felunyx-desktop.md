# Native Felunyx Desktop Architecture

## Purpose

The native Felunyx Desktop exists to realize behaviors that are difficult to maintain consistently as layers over unrelated desktops: per-workspace organization modes, transversal stacks, monitor-local dynamic workspaces, exact Set restoration, and one coherent shell.

It is a long-term component, not a prerequisite for the first useful Felunyx release.

## Technology

- Wayland-only official session
- Rust-first compositor and policy code
- Smithay technology lineage when validated by the prototype
- mature compositor foundation rather than a bare-Smithay implementation by default
- `pop-os/cosmic-comp` as the preferred first Phase 8 prototype foundation
- Qt 6
- QML/Qt Quick
- XWayland on demand
- typed D-Bus services
- standard portals
- custom Wayland protocols only for compositor-owned behavior
- CXX-Qt only where an in-process Rust/Qt object model is justified

`cosmic-comp` is a provisional implementation foundation, not the Felunyx desktop product. Felunyx does not adopt the COSMIC shell, visual language, settings model, or private services merely because they are present in the upstream compositor stack.

## Compositor foundation strategy

Felunyx applies selective ownership to the compositor itself: reuse mature upstream infrastructure that does not define the Felunyx experience, and own the policy that does.

The preferred prototype begins from a pinned, known-good `cosmic-comp` revision. Before that foundation can become long-term architecture, the prototype must prove three things:

1. **Decoupling:** COSMIC-specific configuration, protocols, settings-daemon integration, presentation libraries, and shell assumptions can be kept, replaced, or removed with explicit rationale rather than silently becoming Felunyx platform contracts.
2. **Product control:** Felunyx can own workspace, layout, stack, focus, rule, restoration, and Work Environment behavior without invasive rewrites of unrelated low-level backend code.
3. **Sustainable inheritance:** a newer upstream revision can be integrated at acceptable cost, with the Felunyx delta remaining measurable and generic fixes having a plausible upstream path.

The compositor is therefore treated as two conceptual ownership zones.

### Upstream-derived foundation

Felunyx should minimize unnecessary divergence in:

- DRM/KMS and device discovery;
- GBM/EGL and renderer plumbing;
- low-level libinput and seat integration;
- output enumeration and mode setting;
- frame and presentation primitives;
- standard Wayland protocol support;
- XWayland lifecycle and generic compatibility plumbing;
- direct-scanout and cursor/surface plumbing;
- hardware quirks that are not Felunyx product policy.

When a change in this zone is generally useful, upstream contribution is preferred over a Felunyx-only patch.

### Felunyx compositor policy

Felunyx deliberately owns:

- stable output, workspace, window, and stack identities;
- monitor-local dynamic workspace behavior;
- Floating, Snap, Tiling, Rolling, and Monocle modes;
- transversal stacks and tab semantics;
- deterministic mode transitions and previews;
- focus and placement policy;
- application rules that organize but do not launch;
- compositor-side Work Environment integration;
- compositor-owned serialization and restoration;
- semantic state exposed to shell and platform services;
- Felunyx-specific compositor protocols only where standard protocols cannot express required behavior.

KWin, Niri, and other mature compositors remain comparison and fallback references. If `cosmic-comp` fails the decoupling, compatibility, or maintenance gates, Phase 8 must compare alternatives instead of forcing the fork through.

## Process boundaries

### Compositor

Owns:

- Wayland server;
- outputs;
- input;
- rendering coordination;
- window and surface lifecycle;
- workspace model;
- primary organization modes;
- stack geometry;
- focus;
- compositor-specific protocols;
- XWayland lifecycle;
- state required to survive shell restart.

Does not own package policy, system updates, or general settings persistence.

### Shell

Qt/QML process owning:

- panel/taskbar;
- launcher;
- overview;
- notifications UI;
- quick controls;
- calendar;
- mode-switch preview;
- workspace interactions.

The shell is Felunyx-owned even when the compositor derives from `cosmic-comp`. A shell crash does not terminate compositor-managed applications.

### Settings

Separate Qt/QML application using platform and compositor interfaces.

It exposes all official behavior, including advanced sections, provenance, preview, Apply/Cancel, shortcut remapping, and configuration export/import.

### Central

Separate Qt/QML application for health, packages, updates, recent actions, and recovery.

It never executes privileged operations directly from QML.

### Platform services

Rust services for:

- config;
- sessions;
- Sets;
- rules;
- packages;
- snapshots;
- system health;
- action journal;
- reboot state.

### Greeter and lock

Separate surfaces with shared visual tokens but strict session and privilege boundaries.

## Internal compositor model

### Stable identities

Outputs, workspaces, windows, and stacks use stable internal identities. Visible workspace numbering is presentation only.

### Workspace state

A workspace contains:

- primary mode;
- ordered windows and stacks;
- active item;
- main-window identity where applicable;
- mode-specific geometry;
- gap policy;
- monitor association;
- name and pin state;
- configuration references.

### Strategy boundary

Each primary mode implements a common layout strategy contract conceptually responsible for:

- insert;
- remove;
- resize;
- promote;
- reflow;
- preview;
- serialize;
- restore;
- validate minimum sizes.

Exact Rust traits are defined during the desktop implementation plan, after the prototype clarifies data ownership and inherited compositor boundaries.

### Stacks

Stacks are model entities, not visual tab widgets attached after layout.

Every layout strategy treats a stack as one placeable item while the stack owns tab order, active tab, attention state, and detach behavior.

## Mode transitions

A transition is planned before it is applied.

Inputs:

- source mode;
- destination mode;
- current geometry;
- stacks;
- active window;
- user choice to preserve or separate stacks;
- user choice to preserve or recalculate proportions;
- monitor work area and constraints.

Output:

- a previewable proposed layout;
- warnings for major changes;
- whether explicit confirmation is required.

Small predictable reflows may apply directly during ordinary insertion. Mode changes always use explicit Apply.

## Shell/compositor protocol

The shell needs structured access to:

- workspace diagrams;
- monitor groups;
- current mode;
- preview proposals;
- stack tabs and attention;
- mode apply/cancel;
- drag targets;
- taskbar window groups;
- overview actions.

The protocol sends semantic state rather than screenshots.

Security-sensitive operations remain authenticated through appropriate system services, not compositor convenience protocols.

No COSMIC-specific private interface is adopted as a stable Felunyx public contract merely because it exists in the prototype foundation.

## Rendering and design system

QML provides the authored surfaces. The compositor provides window composition and any protocol-level effects.

The shared `Felunyx.UI` module defines:

- colors and semantic tokens;
- typography;
- density;
- radii;
- frosted-surface recipe;
- noise;
- borders;
- shadows;
- motion durations and curves;
- controls;
- focus;
- accessibility;
- icon language.

Effects must degrade cleanly when unsupported or disabled.

## Input and accessibility

Required prototype coverage:

- keyboard;
- pointer;
- touch where supported;
- touchpad gestures;
- tablet and pen;
- input methods;
- screen readers through the chosen accessibility stack;
- reduced motion;
- high contrast;
- fractional scaling;
- multiple refresh rates;
- portrait output.

Focus-follows-cursor is optional and includes a configurable delay. Click-to-focus is default.

## Compatibility

### XWayland

Starts on demand. Settings can expose per-application compatibility exceptions such as scaling or decoration behavior.

Central or Settings may identify that an application runs through XWayland without treating compatibility as an error.

### Portals

Screen sharing, capture, file selection, and sandbox permissions use standard portals. Recording and remote-control state always has a visible indicator.

### Applications

Session restoration uses application-native mechanisms first. The compositor does not pretend it can reconstruct arbitrary internal application state.

## Prototype gate

Phase 8 begins from a pinned mature compositor baseline rather than assuming a new compositor skeleton must be assembled from bare Smithay.

The prototype sequence must:

1. build and run a known-good upstream `cosmic-comp` revision without Felunyx changes;
2. prove nested and TTY launch on the declared test matrix;
3. establish a repeatable upstream-sync baseline;
4. inventory COSMIC-specific configuration, protocol, settings-daemon, shell, and presentation coupling;
5. replace or bridge only enough of that coupling to start a minimal Felunyx Qt/QML shell;
6. prove Wayland and XWayland applications survive shell restart;
7. implement at least one clearly Felunyx-specific workspace behavior as a vertical slice;
8. measure and classify the resulting patch delta;
9. integrate a newer upstream revision and measure synchronization cost;
10. decide whether `cosmic-comp` becomes the accepted long-term foundation or whether another mature compositor base should be evaluated.

The architecture is reconsidered if the prototype cannot reasonably support:

- nested and TTY launch;
- two-monitor hotplug;
- fractional scaling;
- XWayland;
- screen sharing and capture;
- input methods;
- tablet input;
- shell restart;
- floating;
- one smart tiling layout;
- one Felunyx-specific nontrivial layout path such as Rolling;
- stacks;
- deterministic serialization and restore;
- a clean Qt/QML shell boundary;
- sustainable upstream synchronization.

Rust + Smithay is the preferred lineage and `cosmic-comp` is the preferred first foundation, but neither preference overrides implementation evidence.
