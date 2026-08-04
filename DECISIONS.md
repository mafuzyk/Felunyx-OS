# Felunyx OS Decision Register

This register records project decisions made before implementation. A later Architecture Decision Record may supersede an entry, but no implementation should quietly contradict it.

Statuses:

- **Accepted** — current canonical direction
- **Provisional** — recommended default, to be validated in its implementation phase
- **Deferred** — intentionally decided later with an explicit trigger
- **Superseded** — retained for history and linked to its replacement

## Core system

| ID | Status | Decision |
|---|---|---|
| D-001 | Accepted | Felunyx is based directly on Arch Linux. |
| D-002 | Accepted | Felunyx uses `systemd`. |
| D-003 | Accepted | Felunyx is a rolling-release distribution. |
| D-004 | Accepted | The Felunyx repository has priority over Arch repositories, but contains only justified native, patched, adapted, or curated packages. |
| D-005 | Accepted | Linux Zen is the default kernel and Linux LTS is installed as a fallback. |
| D-006 | Accepted | Automatic installations use Btrfs with separated system and home scopes. |
| D-007 | Accepted | System restoration preserves home by default. Restoring home first creates a safety snapshot. |
| D-008 | Accepted | Felunyx ships one ISO with a deeply customized Calamares installer. |
| D-009 | Accepted | GRUB is recommended by default; Limine is an official alternative; exactly one is installed. |
| D-010 | Accepted | One graphical profile is selected during installation. |

## Desktop profiles and platform

| ID | Status | Decision |
|---|---|---|
| D-011 | Accepted | KDE Plasma is the first reference desktop and initial implementation target. |
| D-012 | Accepted | XFCE and Hyprland are official profiles added after the shared platform stabilizes. |
| D-013 | Accepted | The native Felunyx Desktop is not on the critical path for the first usable distribution release. |
| D-014 | Accepted | All official profiles share Felunyx services, Central, Settings, recovery, design tokens, and session concepts. |
| D-015 | Accepted | Official functionality must be available through a high-quality GUI. Configuration files are optional advanced interfaces, not requirements. |
| D-016 | Accepted | GUI and CLI use the same backend and expose the same transaction evidence. |
| D-017 | Accepted | Configuration inheritance is `Global → Monitor → Workspace → Set → Application`. |
| D-018 | Accepted | The GUI displays configuration provenance and uses “Restore inherited value.” |

## Native Felunyx Desktop

| ID | Status | Decision |
|---|---|---|
| D-019 | Accepted | The official native session is Wayland-only, with XWayland started on demand for compatibility. |
| D-020 | Accepted | The compositor is written in Rust on Smithay. |
| D-021 | Accepted | Shell and graphical system applications use Qt 6/QML. |
| D-022 | Accepted | QML owns presentation; Rust owns state, validation, policy, and privileged behavior. |
| D-023 | Accepted | Compositor, shell, Central, Settings, greeter, and services are separate failure domains. |
| D-024 | Accepted | D-Bus is used for typed services, standard portals for sandbox integration, and Wayland protocols for compositor-specific behavior. |
| D-025 | Accepted | A shared `Felunyx.UI` module defines the visual system. |

## Window management

| ID | Status | Decision |
|---|---|---|
| D-026 | Accepted | Each workspace has exactly one primary mode: Floating, Snap, Tiling, Rolling, or Monocle. |
| D-027 | Accepted | Stacking is transversal and compatible with every primary mode. |
| D-028 | Accepted | Mode changes preview the whole workspace and require explicit application. |
| D-029 | Accepted | Floating is the first-use default. |
| D-030 | Accepted | Smart Tiling preserves a stable main area when focus changes. A new main window is explicitly promoted. |
| D-031 | Accepted | Rolling defaults to horizontal on landscape monitors and vertical on portrait monitors. |
| D-032 | Accepted | A new window added to a stack does not steal focus. |
| D-033 | Accepted | Dragging a tab out reinserts it according to the workspace’s primary mode. |
| D-034 | Accepted | One-level session-temporary layout undo may be enabled, but is disabled by default. |
| D-035 | Accepted | Direct mode shortcuts exist but are disabled by default and fully remappable. |

## Workspaces and monitors

| ID | Status | Decision |
|---|---|---|
| D-036 | Accepted | Workspaces are dynamic and independent per monitor. |
| D-037 | Accepted | One empty trailing workspace is maintained. Empty intermediate workspaces disappear. |
| D-038 | Accepted | Naming a workspace does not pin it. Pinning is explicit. |
| D-039 | Accepted | Overview uses abstract layout diagrams rather than live thumbnails by default. |
| D-040 | Accepted | Workspaces from a disconnected monitor move temporarily to the primary display while retaining source identity. |
| D-041 | Accepted | Reconnecting a known monitor asks before restoration by default; an automatic per-monitor policy is available. |
| D-042 | Accepted | Workspace naming suggestions are local, optional, and never applied automatically. |

## Rules, Sets, and sessions

| ID | Status | Decision |
|---|---|---|
| D-043 | Accepted | Ordinary application rules organize windows after launch; they never launch applications. |
| D-044 | Accepted | Sets may launch applications and restore workspaces, layouts, documents, projects, and tabs. |
| D-045 | Accepted | Approved rules may create missing destination workspaces without asking again. |
| D-046 | Accepted | A Set previews its effects and reuses already-open applications where possible. |
| D-047 | Accepted | Leaving a Set restores temporary configuration and never terminates applications without confirmation. |
| D-048 | Accepted | Session restoration prefers exact application state when the application supports it. |
| D-049 | Accepted | Sensitive and private application contexts are excluded from restoration by default. |
| D-050 | Accepted | Login session restoration supports Ask, Automatic, and Never policies. |

## Shell and interaction

| ID | Status | Decision |
|---|---|---|
| D-051 | Accepted | The bottom bar behaves as an authored modern taskbar, not a generic panel. |
| D-052 | Accepted | Intelligent autohide is the default and reveals the bar progressively near the screen edge. |
| D-053 | Accepted | The bar uses restrained frosted glass, fine noise, subtle border, and adaptive opacity. |
| D-054 | Accepted | Tray items are collapsed by default; quick controls and notifications are separate panels. |
| D-055 | Accepted | Notification popups appear above the lower-right bar area, with at most three visible. |
| D-056 | Accepted | Dismissed notifications do not enter a hidden permanent history. |
| D-057 | Accepted | Only Felunyx or the user may pin a notification. Applications cannot self-pin. |
| D-058 | Accepted | The clock shows time above date and follows locale unless overridden. |
| D-059 | Accepted | The launcher is traditional and compact, but must not visually copy the Windows Start menu. |
| D-060 | Accepted | Launcher home shows separate Fixed and Recent application grids; files appear only in search. |
| D-061 | Accepted | “All applications” is a separate launcher view. |
| D-062 | Accepted | The default desktop has no icons; icons, folders, and widgets remain optional. |
| D-063 | Accepted | Window controls stay on the right with a thin, integrated titlebar. |

## Packages and updates

| ID | Status | Decision |
|---|---|---|
| D-064 | Accepted | Default source priority is Felunyx → Arch → curated AUR → Flatpak → Nix. |
| D-065 | Accepted | The user may override a source recommendation and sees the reason for the default. |
| D-066 | Accepted | AUR updates join the same user-facing transaction while retaining a distinct build and verification stage. |
| D-067 | Accepted | AUR packages are built, checked, and signed by Felunyx infrastructure where available; clients validate signatures and metadata freshness. |
| D-068 | Accepted | Failed verification blocks the affected version in the managed layer. |
| D-069 | Accepted | Full system updates always show the plan and require confirmation. |
| D-070 | Accepted | The CLI requires an explicit `--assume-yes`-style flag for non-interactive confirmation. |
| D-071 | Accepted | Risk classification combines curated critical packages, dependency impact, and special rules. |
| D-072 | Accepted | Risk levels are Low, Moderate, and High. |
| D-073 | Accepted | Automatic snapshot modes are Smart, Always, and Never; Smart is the default. |
| D-074 | Accepted | Reboot-pending state identifies the component that requires restart and persists until the new state is validated. |
| D-075 | Accepted | No background repair process silently changes the system. |

## Recovery

| ID | Status | Decision |
|---|---|---|
| D-076 | Accepted | Recovery categories are Boot, System, Storage, Packages, and Diagnostics. |
| D-077 | Accepted | Recovery follows Analysis → Proposal → Confirmation → Result. |
| D-078 | Accepted | Proposed recovery commands are displayed directly before execution. |
| D-079 | Accepted | Boot failure asks the user among LTS, snapshot, repair, recovery, and power options; it does not auto-select by timeout. |
| D-080 | Accepted | Recovery provides a full terminal. |
| D-081 | Accepted | Networking is available by default; remote access and report submission remain off without consent. |
| D-082 | Accepted | Recovery retains Felunyx identity but prioritizes contrast, stability, and low graphical complexity. |

## Identity and project structure

| ID | Status | Decision |
|---|---|---|
| D-083 | Accepted | The brand is “Felunyx”; “Felunyx OS” is the formal distribution name. |
| D-084 | Accepted | The visual foundation is graphite with restrained blue/violet accents and a subtle ethereal edge. |
| D-085 | Accepted | The lynx mark balances geometric minimalism with expressive stylization. |
| D-086 | Accepted | StartAllBack is an ergonomic launcher/taskbar reference only, never a direct visual reference. |
| D-087 | Accepted | The project begins as a phased monorepo. Components split into separate repositories only when ownership, release cadence, or access requirements justify it. |
| D-088 | Accepted | The repository is licensed under GPL-3.0 unless a component states another compatible license. |
| D-089 | Accepted | Work pauses at every phase boundary for review. |

## Provisional defaults to validate during implementation

| ID | Status | Decision |
|---|---|---|
| D-090 | Provisional | Disk encryption is prominently recommended in automatic installation but remains an explicit user choice. |
| D-091 | Provisional | A host firewall is enabled with a conservative desktop policy. |
| D-092 | Provisional | Telemetry is absent by default; any future diagnostics program must be opt-in, inspectable, and separately approved. |
| D-093 | Provisional | Secure Boot support is a release objective, but is not advertised until installation, update, kernel fallback, and recovery paths are automated and tested. |
| D-094 | Provisional | The first internal ISO implements KDE only; XFCE and Hyprland enter after platform contracts stabilize. |
| D-095 | Provisional | The package CLI placeholder is `fel`; the final command name is chosen before its public interface freezes. |

## Explicitly deferred decisions

| ID | Status | Trigger |
|---|---|---|
| D-096 | Deferred | Exact Btrfs subvolume names are chosen in Phase 2 when the image and installer tests exist. |
| D-097 | Deferred | Exact Rust crate, D-Bus interface, and database names are chosen in the owning component specifications. |
| D-098 | Deferred | Stable/testing/development channel topology is finalized in Phase 7 after build and repository operating costs are measured. |
| D-099 | Deferred | The native desktop’s first public channel is chosen only after nested, TTY, multi-monitor, XWayland, portal, input-method, and tablet prototypes pass. |
| D-100 | Deferred | Exact default applications are selected during the KDE reference phase using integration, accessibility, maintenance, and source-policy criteria. |

## Additional accepted defaults

| ID | Status | Decision |
|---|---|---|
| D-101 | Accepted | Set activation preserves the current arrangement and opens or reuses additional Set workspaces by default; replacing the current arrangement is an explicit preview choice. |

## Changing a decision

A change must:

1. identify the decision ID;
2. explain the evidence or constraint that changed;
3. describe migration and compatibility effects;
4. add or update tests where the decision affects behavior;
5. mark the old decision Superseded rather than erasing history.
