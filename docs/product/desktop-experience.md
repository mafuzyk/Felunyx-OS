# Felunyx Desktop Experience

## Scope

This document defines the intended desktop experience shared conceptually across official profiles and implemented natively by the future Felunyx Desktop.

It is not a pixel-perfect theme specification. It records interaction, hierarchy, identity, and behavior that should survive implementation changes.

## Visual language

Felunyx uses:

- a neutral graphite foundation;
- restrained blue and violet accents;
- frosted surfaces rather than clear glass;
- fine noise and nearly invisible inner borders;
- short, soft shadows;
- compact density by default;
- deliberate whitespace rather than oversized controls;
- fast, functional motion;
- a subtle ethereal quality that never reduces legibility.

The interface remains usable when blur, transparency, and animation are disabled.

### Avoid

- neon gaming motifs;
- decorative glow as a focus indicator;
- excessive rounded cards;
- giant mobile-like controls on desktop;
- generic enterprise dashboard structure;
- direct platform imitation;
- surfaces that become unreadable over bright wallpapers;
- animations whose only purpose is to delay state changes.

## Default desktop

The default desktop is clean and contains no icons. Desktop icons, folders, and widgets are supported options.

The panel/taskbar sits at the bottom and adapts between a slightly floating desktop form and a more edge-integrated form when windows are maximized.

## Panel and taskbar

### Layout

Default order:

1. Felunyx launcher;
2. pinned applications;
3. open application groups;
4. tray/status area;
5. notifications;
6. clock and date.

Applications use compact grouped icons. State indicators are subtle but visible.

### Interaction

- primary click focuses or cycles the group;
- hover shows previews;
- middle click starts a new instance;
- context menu exposes application and window actions;
- grouping is configurable;
- modules can be reordered;
- size, spacing, alignment, transparency, and grouping are configurable through the GUI.

### Visibility modes

- **Intelligent** — default; hides for maximized, fullscreen, or overlapping windows
- **Fixed**
- **Automatic**
- **Overlay**

Intelligent reveal begins with a tiny edge hint as the pointer approaches. The full bar appears after a short deliberate delay, approximately 200–300 ms. When revealed, it overlays the workspace instead of resizing windows.

### Appearance

The default bar is graphite, semi-transparent, softly blurred, lightly textured, and bordered. Accent can be fixed to the Felunyx identity or adapted from the wallpaper.

## Launcher

The launcher is a **compact personal panel**, not a Start menu clone.

StartAllBack informs ergonomic density and practicality only. The Felunyx launcher must not copy Windows proportions, two-column hierarchy, “Recommended” content, energy-button layout, tiles, or visual rhythm.

### Home view

- circular avatar without a permanent large account header;
- name shown on hover or account interaction;
- universal search available but not visually dominant;
- separate compact **Fixed** and **Recent applications** grids;
- Recent contains applications only, never recent documents;
- side modules for folders, Central, Settings, and Sets;
- compact session and energy controls.

### Search

Search may find:

- applications;
- files;
- folders;
- settings;
- safe system actions;
- Sets.

Files do not leak into the default launcher home.

### All applications

“All applications” replaces the home view inside the launcher. It uses a compact alphabetical grid and an explicit back action. It is not appended as an endless list beneath the home content.

### Identity

The launcher appears to emerge from the bar through a short spatial transition. Its surfaces, icon treatment, typography, and module rhythm are Felunyx-specific.

A successful result is familiar within seconds but not mistaken for Windows.

## Window decoration

- thin integrated titlebar/toolbar;
- title aligned left;
- minimize, maximize/restore, and close aligned right;
- controls remain low contrast until the pointer enters the titlebar;
- close uses a restrained warm state only on hover;
- restored windows have soft corners;
- maximized windows have square outer corners;
- maximization reduces redundant titlebar space;
- official height options are Compact, Standard, and Expanded.

## Window organization

Each workspace uses one primary mode.

### Floating

Traditional free placement. First-use default.

### Snap

Traditional halves and quarters plus suggested layouts.

### Tiling

Smart Tiling considers the whole workspace, minimum sizes, orientation, main-window role, stacks, and balance.

Focus changes never resize the layout. The main area stays stable until a window is explicitly promoted.

Manual resize first affects nearest neighbors. Global redistribution happens only when minimum constraints require it.

### Rolling

A continuous strip:

- horizontal by default on landscape;
- vertical by default on portrait;
- overridable per monitor, workspace, or Set;
- freely resizable;
- resizing pushes neighbors and preserves continuity.

### Monocle

One primary visible window. Gaps disappear.

### Stacking

Stacking is compatible with all modes.

Tabs appear only with multiple windows and show:

- application icon;
- short title;
- activity dot;
- close, detach, reorder, and move actions.

Dragging a window over another previews grouping across the target, but the strong confirmation region is near the titlebar/tab area. Hover never creates a stack.

A new window entering a stack does not steal focus. Closing the active tab returns to the previously used tab, or the nearest tab when no history exists. A one-window stack dissolves automatically.

Dragging a tab out reinserts it according to the workspace’s primary mode.

## Mode switch preview

Changing a workspace mode opens a translucent preview over the current context.

The user can:

- select a primary mode through visual miniatures;
- inspect the proposed arrangement;
- drag and resize proposal regions;
- choose globally whether stacks are preserved or separated;
- choose whether proportions are preserved or recalculated;
- apply or cancel.

No mode change occurs merely by hovering or selecting a miniature.

## Overview

Overview is per monitor:

- horizontal strip on landscape monitors;
- vertical strip on portrait monitors;
- abstract layout diagrams rather than live thumbnails;
- optional application icons;
- stack and main-area structure visible;
- dynamic trailing empty workspace.

This improves performance and privacy while still communicating organization.

## Quick controls

Quick controls are separate from notifications.

Default density is Compact, with Comfortable and Large alternatives.

Common controls include:

- Wi-Fi;
- Bluetooth;
- audio output and volume;
- brightness;
- battery and energy;
- Focus mode.

Contextual controls appear only when relevant unless pinned.

## Notifications

### Popup behavior

- lower right above the bar;
- stack upward;
- maximum three visible;
- additional count shown as `+N`;
- hover pauses expiration;
- critical and pinned notifications do not expire.

Approximate timing adapts to content:

- simple status: around 4 seconds;
- text: 6–8 seconds;
- actions: longer;
- progress: while relevant.

### Notification center

Separate panel with:

- grouped-by-application default;
- chronological toggle;
- older groups collapsed automatically;
- at most two quick actions visible;
- inline expanded reply;
- important notifications pinned until resolved or cleared.

Only Felunyx or the user can pin. Applications cannot self-pin.

Dismissed notifications disappear rather than moving into a hidden permanent history.

### Privacy

Per-application lock-screen levels:

- Private — application and count;
- Summary — sender/title;
- Full — declared content.

Sensitive actions require unlock.

## Calendar and clock

The taskbar clock shows time above date.

Locale selects 12/24-hour display and date format, with user override.

The calendar:

- starts Monday by default;
- shows a discreet week number;
- uses a small dot for events;
- distinguishes holidays through restrained typography;
- has a Today action;
- shows one selected day’s events in a compact internal side panel;
- displays “No events” when empty;
- opens the default calendar application when an event is selected;
- does not include an unnecessary create button.

## Sounds

No boot, login, or shutdown sound.

Notification sound policy may use:

- Felunyx category sounds;
- application sound;
- no sound;
- per-application choice.

Categories include message, completion, warning, error, critical, and connectivity. Sounds are short, technical, minimal, and subtly ethereal.

## Accessibility

All official surfaces must support:

- keyboard navigation;
- visible focus without relying only on color;
- screen-reader labels;
- scalable text;
- reduced motion;
- disabled blur/transparency;
- high contrast;
- configurable density;
- remappable shortcuts;
- no required pointer-only gesture.

Accessibility is part of the main interface, not a separate downgraded mode.
