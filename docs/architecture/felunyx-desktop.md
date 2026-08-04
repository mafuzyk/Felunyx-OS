# Native Felunyx Desktop Architecture

## Purpose

The native Felunyx Desktop exists to realize behaviors that are difficult to maintain consistently as layers over unrelated desktops: per-workspace organization modes, transversal stacks, monitor-local dynamic workspaces, exact Set restoration, and one coherent shell.

It is a long-term component, not a prerequisite for the first useful Felunyx release.

## Technology

- Wayland-only official session
- Rust
- Smithay
- Qt 6
- QML/Qt Quick
- XWayland on demand
- typed D-Bus services
- standard portals
- custom Wayland protocols only for compositor-owned behavior
- CXX-Qt only where an in-process Rust/Qt object model is justified

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

A shell crash does not terminate compositor-managed applications.

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

Exact Rust traits are defined during the desktop implementation plan, after the prototype clarifies data ownership.

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

The desktop architecture is reconsidered if the prototype cannot reasonably support:

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
- one rolling layout;
- stacks;
- deterministic serialization and restore.

Choosing Smithay is an accepted direction, not permission to ignore evidence from implementation.
