# Felunyx Work Environments Design

**Status:** Proposed after direction approval on 2026-08-05; written specification pending Mafu review.

**Phase ownership:** Isolated preparation while Phase 2 remains active. Backend ownership begins only after the Phase 2 review authorizes Phase 3. KDE product work belongs to Phase 4, profile parity to Phase 6, and native-desktop completeness to Phase 8.

## 1. Purpose

Felunyx should organize the computer around durable areas of work while preserving the project's existing promises of transparency, reversibility, privacy, and shared GUI/CLI consequences.

A **Work Environment** is a persistent, named work context that can associate:

- applications;
- files, directories, projects, URLs, and application-native sessions;
- monitor-local workspaces and window organization;
- temporary rules;
- focus and notification policy;
- audio, energy, performance, network, Bluetooth, and device preferences where supported;
- capability and restoration evidence;
- privacy exclusions;
- activation history and recovery information.

The feature is not a script launcher, a theme preset, or a promise to copy arbitrary process memory. It coordinates supported mechanisms and reports exactly what was restored, approximated, skipped, or failed.

The product promise is:

> Felunyx restores what it can identify and validate, preserves the person's work, and states the real support level of every restored item.

## 2. Relationship to canonical Sets

The current canonical documents define a **Set** as a named temporary working context. Decisions D-043 through D-050 and D-101 remain authoritative until explicitly superseded.

This design proposes a refinement rather than a silent replacement:

- **Work Environment** becomes the public product concept.
- A Work Environment is persistent even while none of its runtime resources are open.
- Temporary Set-like configuration remains one part of a Work Environment.
- Rules still organize and never launch applications.
- Work Environments remain the only ordinary Felunyx automation allowed to launch applications.
- Activation still previews effects and preserves the existing arrangement by default.
- Leaving or closing an Environment never discards work or terminates applications without confirmation.

Approval of this written specification will require a later, explicit decision-register update. Until that update, implementations must continue to follow the existing Set terminology and semantics.

## 3. Scope and non-goals

### 3.1 In scope

- persistent Environment definitions;
- multiple open Environments in one login session;
- one primary active Environment per login session in the initial design;
- activation analysis, preview, confirmation, execution, validation, and result;
- application and desktop capability reporting;
- resource reopening through supported application mechanisms;
- application-native session delegation;
- deterministic window and workspace organization where the active desktop can provide it;
- temporary preferences with explicit prior state and reversal;
- privacy-sensitive exclusions;
- structured partial failure;
- portable definitions across official Felunyx desktop profiles;
- stronger behavior in the native Felunyx Desktop without making it a prerequisite for the first usable release.

### 3.2 Explicit non-goals

The first design does not promise:

- universal recovery of unsaved application memory;
- private-browsing restoration;
- arbitrary editing of undocumented application configuration;
- perfect window identity from titles alone;
- identical behavior across KDE, XFCE, Hyprland, and the native desktop;
- multiple simultaneously active global policy contexts;
- scripts with hidden or ambient authority;
- application forks merely to support Environments;
- a frozen public D-Bus, database, crate, or plugin interface before its owning phase approves one.

## 4. Runtime states

A Work Environment has one of three user-visible runtime states.

### 4.1 Closed

The persistent definition exists, but no live runtime is associated with it.

Closing an Environment is explicit. If associated applications, documents, or workspaces are still live, Felunyx previews what will happen. The default is to leave user work open and detach it from Environment-owned temporary policy rather than terminate anything.

### 4.2 Open in background

The Environment has live resources, windows, or workspaces, but it is not the primary current context.

Open-in-background Environments retain:

- resource and window associations;
- Environment-owned workspace identity where supported;
- rules required to keep their live layout coherent;
- restoration evidence and partial-failure state.

They do not retain active-only global preferences such as focus mode, global audio routing, or power policy unless the user promotes those values to another configuration scope.

### 4.3 Active

The active Environment is open and receives the primary session-wide temporary policy layer.

The initial product supports one active Environment per login session because global notification, audio, network, energy, and performance policies need deterministic conflict resolution. Multiple Environments may remain open in the background.

Changing the active Environment does not destroy or close the previous one. It normally moves the previous Environment to the background and reverses only its active-only temporary values.

## 5. Configuration lifetimes

Environment-controlled values are divided by lifetime.

### 5.1 Definition values

Persistent instructions stored in the Environment, such as desired projects, applications, workspace names, or preferred audio device.

### 5.2 Open-lifetime values

Temporary rules needed while the Environment remains open, such as routing a newly created Krita window to the Environment's Drawing workspace.

### 5.3 Active-only values

Temporary global or session preferences that apply only while the Environment is active, such as focus mode, performance policy, default audio route, or notification filtering.

### 5.4 Promoted values

The user may explicitly promote a temporary value into Global, Monitor, Workspace, or Application scope. Promotion is a separate previewed action and is never inferred from repeated activation.

The existing inheritance order becomes conceptually:

`Global -> Monitor -> Workspace -> Work Environment -> Application`

The exact decision-register wording remains pending review because canonical documents currently name the Set layer.

## 6. Capability model

Support is not represented by one misleading "compatible" flag. Every application and desktop adapter reports independent capabilities.

### 6.1 Application capabilities

- **Launch:** start or reuse the application.
- **Open resources:** open files, directories, projects, workspaces, URLs, or profiles.
- **Native session:** request or rely on the application's supported session restoration.
- **Window correlation:** associate resulting windows with the requested Environment items.
- **Preference control:** apply and reverse documented application preferences.
- **Unsaved-state support:** report whether the application itself provides autosave or crash/session recovery; Felunyx does not fabricate this capability.
- **Sensitive-context detection:** identify private, authentication, password, banking, or user-marked sensitive contexts when reliable evidence exists.

### 6.2 Desktop capabilities

- create or reuse workspaces;
- preserve stable workspace identity;
- associate workspaces with Environments;
- position and size windows;
- manage stacks or desktop-specific groupings;
- preserve monitor identity;
- restore layouts deterministically;
- apply temporary rules;
- expose capability loss before activating an Environment created on another profile.

### 6.3 Capability states

Each capability is reported as:

- **Supported and validated**;
- **Supported with limitations**;
- **Provided by the application or desktop**;
- **Unavailable**;
- **Unknown or not yet tested**.

Static configuration never upgrades an unknown capability to validated runtime support.

## 7. Feasible initial application integrations

Initial integrations should prefer applications whose official interfaces already cover useful work.

### 7.1 Krita

A practical first adapter may:

- open saved `.kra` resources;
- reuse an existing Krita process where normal application behavior allows it;
- request a named Krita workspace through its documented command-line option;
- delegate internal document/session recovery to Krita;
- correlate resulting top-level windows and place them through the desktop adapter.

Felunyx does not claim generic recovery of canvas changes that Krita itself has not saved or retained.

### 7.2 Code editors

A practical editor adapter may:

- open a file, directory, or native workspace;
- request an application profile when the editor documents one;
- rely on the editor's own tab, terminal, and session restoration;
- place resulting top-level windows;
- report partial restoration when the editor restores a different internal state than requested.

The initial product may validate VS Code as one reference integration, but the Environment model must not depend on VS Code-specific storage.

### 7.3 File managers

A generic integration may reopen known directories and place resulting windows. Tabs are restored only when the selected file manager exposes a supported session mechanism.

### 7.4 Terminals

A basic terminal integration may restore:

- executable or desktop entry;
- initial working directory;
- shell profile when documented;
- an explicitly requested command after visible review.

Felunyx must not store terminal screen content or secret-bearing command history as Environment state by default.

### 7.5 Browsers

Normal browser resources may be restored through documented profiles, URLs, or browser-native sessions.

Private windows, authentication windows, banking contexts, and user-marked sensitive profiles are excluded by default. The Environment records that a private item was excluded, not its content or URL.

## 8. Application integration rules

An application integration may use only supported mechanisms such as:

- standard URI or file opening;
- documented command-line options;
- documented D-Bus interfaces;
- stable, documented configuration schemas;
- application-native session mechanisms;
- an optional plugin maintained and reviewed for that application;
- future standard desktop or Wayland session contracts after validation.

An integration must not:

- scrape arbitrary widget text;
- read another process's private memory;
- synthesize save shortcuts;
- edit undocumented internal storage and call it stable;
- retain secrets in logs;
- report successful internal restoration based only on a top-level window appearing.

## 9. Window correlation

Application identity alone is insufficient when multiple similar windows exist. Felunyx combines evidence instead of trusting titles.

Possible evidence includes:

1. the application and resource requested by the activation plan;
2. process or instance correlation where meaningful;
3. activation tokens or launch correlation supplied by the desktop session;
4. window creation timing as supporting evidence, never the sole identity;
5. application identity such as desktop entry or Wayland application identity;
6. supported application integration data;
7. document or project title as secondary evidence only;
8. prior user-confirmed association.

A match result is:

- **Confirmed**;
- **Probable, confirmation required before sensitive movement**;
- **Ambiguous**;
- **Unmatched**.

Ambiguous windows remain in place unless the preview or user action resolves them. Felunyx does not move an unrelated window merely because its title resembles a saved document.

## 10. Activation pipeline

Activation uses the same transparent product language as system transactions.

### 10.1 Analysis

Read-only analysis determines:

- available applications and sources;
- referenced resource existence and access;
- application and desktop capabilities;
- currently open reusable resources;
- monitor and workspace availability;
- current values that temporary policy would override;
- privacy exclusions;
- missing network, device, or service dependencies;
- conflicts with the currently active Environment.

Missing software produces a separate installation proposal. Environment activation never silently installs packages.

### 10.2 Proposal

The preview shows:

- applications reused or launched;
- resources reopened;
- native sessions requested;
- workspaces created or reused;
- windows expected to move;
- temporary values applied and their prior sources;
- unavailable or approximate desktop behavior;
- excluded sensitive items;
- operations that require networking;
- rollback or reversal available for each temporary change.

The user may omit an optional item for this activation without rewriting the persistent Environment definition.

### 10.3 Confirmation

Routine activation may use a concise confirmation policy selected by the user, but these actions always require explicit review:

- closing applications or documents;
- changing network connections;
- changing services;
- running commands;
- applying undocumented or newly introduced integration behavior;
- replacing the current arrangement;
- modifying persistent configuration;
- installing missing software.

### 10.4 Execution

Execution is staged and journaled:

1. establish the Environment runtime record;
2. create or reuse workspaces;
3. apply reversible open-lifetime policy;
4. apply reversible active-only policy;
5. reuse or launch applications;
6. request resource and native-session restoration;
7. correlate and place windows;
8. validate resulting state;
9. write one structured result.

Stages declare dependencies so one failed item does not automatically invalidate unrelated work.

### 10.5 Result

The result groups all outcomes instead of producing a notification storm:

- restored exactly;
- restored by the application;
- restored approximately;
- reused from the current session;
- excluded for privacy;
- skipped by user choice;
- failed with retained evidence;
- still pending an application response;
- not restorable on the current desktop profile.

## 11. Leaving, switching, and closing

### 11.1 Switch active Environment

- validates the target;
- reverses the prior Environment's active-only values;
- applies the target's active-only values;
- retains both Environments' open-lifetime state;
- does not close applications.

### 11.2 Leave to no active Environment

Felunyx may return to inherited Global, Monitor, Workspace, and Application values while keeping one or more Environments open in the background.

### 11.3 Close Environment

The preview distinguishes:

- temporary configuration to reverse;
- Environment-only empty workspaces safe to remove;
- live workspaces that contain user windows;
- applications that can remain open as ordinary session applications;
- applications the user explicitly asked to close;
- unsaved-state warnings provided by the application or desktop.

No application is terminated and no workspace containing user work is deleted without confirmation.

## 12. Updating an Environment

Runtime state and saved definition are separate.

The user may:

- save selected runtime changes into the Environment;
- reject incidental changes;
- remove stale resources;
- add a newly opened project;
- update layout where supported;
- keep application-native session ownership with the application;
- inspect privacy exclusions before saving;
- duplicate or export the definition.

Felunyx never treats every open window as intentional Environment state merely because it was visible when Save was pressed.

## 13. Preference safety

A preference adapter must declare:

- supported versions or schema conditions;
- read mechanism;
- write mechanism;
- prior value and provenance;
- temporary value;
- validation method;
- reversal method;
- failure behavior when the application is running;
- whether restart or reload is required.

Critical configuration writes use atomic replacement where applicable. If validation fails, Felunyx preserves the previous value and reports the failure.

When no stable mechanism exists, the preference is unavailable rather than implemented through brittle file mutation.

## 14. Privacy and sensitive state

Excluded by default:

- private browsing windows;
- password managers;
- banking applications;
- authentication and privilege prompts;
- secret-bearing terminal contexts;
- user-marked sensitive applications, windows, resources, or Environments;
- notification content;
- clipboard contents;
- document contents beyond the resource identifier required to reopen a user-approved saved file.

Logs and exports distinguish metadata from content. A diagnostic export previews categories and redactions before writing.

An Environment may record:

> Two private browser windows were excluded.

It must not record their URLs, titles, account identity, or page content.

## 15. Interrupted and partial activation

The action journal records stage boundaries and enough prior state to analyze interruption.

After interruption, Felunyx proposes one of:

- continue pending independent items;
- retry a failed item;
- reverse temporary policy;
- keep successfully opened resources and stop;
- close the incomplete Environment runtime without terminating user applications.

Felunyx does not rerun commands, reconnect networks, or repeat side effects automatically merely because the previous result is incomplete.

Offline activation remains possible for local resources. Network-dependent items are marked unavailable or deferred without disabling local Environment functionality.

## 16. Cross-profile portability

The persistent Environment definition is desktop-agnostic where possible. Desktop-specific layout information is stored as optional capability-bound data rather than replacing the common definition.

Opening an Environment on another official profile produces a conversion preview:

- common applications and resources remain available;
- unsupported layout modes are approximated or omitted;
- desktop-specific information is preserved for later return;
- the original definition is not rewritten unless the user explicitly saves the conversion;
- capability loss is visible before activation.

Example:

> Rolling layout is unavailable in the KDE reference session. Applications and projects can be restored, while window placement will use the KDE adapter's supported arrangement.

No adapter may bypass platform safety, privacy, confirmation, or journal policy.

## 17. Role of the native Felunyx Desktop

The native desktop is the reference implementation where Work Environment concepts can be represented directly rather than translated.

It is expected to provide, after its own phase gates:

- stable workspace identity;
- explicit workspace-to-Environment ownership;
- reliable window-to-Environment association;
- native Floating, Snap, Tiling, Rolling, Monocle, and stacking behavior;
- monitor hotplug that preserves Environment and source-monitor identity;
- deterministic layout restoration;
- shell restart without compositor or Environment-state loss;
- session-aware activation correlation;
- standard portal integration;
- XWayland compatibility on demand.

The native desktop still does not own application-internal document state. It improves correlation, layout, workspaces, monitor behavior, and session evidence while applications remain responsible for their supported internal sessions.

## 18. Portal and sandbox compatibility

The native desktop treats XDG Desktop Portal support as a required compatibility layer.

The project may compose mature portal backends and implement Felunyx-specific backends only where the desktop owns a required session capability. A new backend must follow the portal project's D-Bus activation and configuration model.

Required validation eventually covers at least:

- file selection and document access;
- URI opening;
- desktop settings exposed through standards;
- screenshots;
- screen casting;
- remote desktop permission flows;
- background execution;
- notifications;
- secret storage integration where selected by the distribution.

Work Environments do not use the portal Settings interface as a generic configuration backend. Portal preferences and Environment policy are separate contracts.

## 19. Performance principles

- no polling loop merely to rediscover unchanged windows when session events are available;
- no GUI process remains resident solely because an Environment exists;
- closed Environments have no active runtime service cost beyond ordinary indexed metadata;
- background Environments retain only the state required for their live resources and rules;
- activation latency and time to first useful window are measured;
- the shell can restart without discarding backend state;
- blur and animation are optional and never required for functional clarity;
- exact budgets are defined from measurements in the owning implementation phases, not invented in this specification.

## 20. Persistence principles

Persistent Environment state is:

- versioned;
- schema-validated;
- migrated explicitly;
- separated from caches and derived window indexes;
- recoverable after failed migration;
- inspectable through official GUI and CLI paths;
- written atomically for critical definition changes;
- exportable without secrets by default.

This design intentionally does not choose an exact database, serialization format, crate, D-Bus name, or public API.

## 21. Phase plan

### Phase 2 — no implementation change

- finish Remote and Virtual evidence;
- review and approve the ISO skeleton;
- keep this document isolated;
- do not merge Work Environment implementation into Phase 2 branches.

### Phase 3 — shared backend minimum

After explicit phase authorization:

- persistent Environment model;
- state machine for Closed, Open, and Active;
- capability registry;
- activation planner;
- action journal;
- temporary configuration reversal;
- application adapter contract;
- desktop adapter contract;
- structured result;
- shared CLI access;
- deterministic fake adapters and contract tests.

Initial real integrations should remain narrow: saved files and URIs, directories, one code-editor reference, Krita `.kra` resources, a terminal working directory, a file manager, and non-private browser resources through supported mechanisms.

### Phase 4 — KDE reference experience

- QML Environment UI;
- create, inspect, open, activate, switch, update, and close flows;
- preview and result surfaces;
- KDE desktop adapter;
- capability matrix;
- accessibility and keyboard navigation;
- Virtual tests for resource reopening, partial failure, window organization, logout/login, and backend restart.

### Phase 5 — recovery, data, and hardware

- Environment-aware recovery evidence;
- hardware and device preference diagnostics;
- external backup as a separate concept from Btrfs snapshots;
- verified backup and restoration state;
- Hardware validation where device policy is advertised.

### Phase 6 — XFCE and Hyprland parity

- profile adapters;
- explicit capability differences;
- conversion previews;
- no cross-profile configuration corruption;
- common terminology and backend policy.

### Phase 8 — native desktop completeness

- native workspace and window ownership;
- monitor and layout fidelity;
- portal matrix;
- XWayland behavior;
- shell failure containment;
- protocol and hardware validation.

## 22. Validation strategy

### Remote — Phase 3

- schema and migration tests;
- state-machine tests;
- capability negotiation tests;
- activation planning fixtures;
- privacy-exclusion tests;
- ambiguous-window tests;
- partial-failure tests;
- journal interruption and reversal tests;
- cross-profile conversion fixtures;
- GUI/CLI proposal equivalence tests;
- no adapter can bypass confirmation policy.

### Virtual — Phase 4 and later

- saved project reopening;
- native editor-session delegation;
- multiple similar windows;
- application already open;
- slow launch;
- helper and dialog windows;
- missing application;
- offline resource activation;
- switching between two open Environments;
- KDE session restart and login restoration;
- partial layout conversion;
- no private resource captured.

### Hardware — Phase 5 and Phase 8

- monitor disconnect and reconnect;
- tablet profile behavior;
- audio device changes;
- Bluetooth and network policy;
- suspend and resume;
- GPU and multi-monitor layout behavior;
- performance and power impact.

Remote evidence never implies desktop runtime behavior, and Virtual evidence never implies physical device reliability.

## 23. Proposed decisions for later canonical review

Approval of this specification should trigger explicit review of these proposals rather than silently editing existing decisions:

1. Use **Work Environment** as the public product term replacing or superseding public **Set** terminology.
2. Define Closed, Open in background, and Active runtime states.
3. Allow multiple open Environments but one active Environment per login session initially.
4. Divide temporary policy into open-lifetime and active-only values.
5. Report application and desktop support through independent capabilities.
6. Delegate unsaved content recovery to application-supported mechanisms; never scrape or fabricate state.
7. Exclude private and sensitive contexts by default.
8. Permit preference changes only through stable, inspectable, reversible mechanisms.
9. Preserve desktop-specific layout data while presenting an explicit conversion preview on other profiles.
10. Make the native Felunyx Desktop the complete reference implementation without placing it on the first-release critical path.
11. Keep backup distinct from snapshot rollback and assign it to a later phase.
12. Require one structured activation result and journal rather than independent notification storms.

## 24. Review gate

Before implementation planning:

- Mafu reviews this written specification;
- terminology and runtime-state behavior are approved or revised;
- conflicts with D-043 through D-050 and D-101 are resolved explicitly;
- accepted changes are entered into `DECISIONS.md` with preserved history;
- affected product and architecture documents are updated;
- Phase 2 reaches its own review boundary;
- Phase 3 is explicitly authorized.

Only after those conditions should a Phase 3 implementation plan choose component names, interfaces, storage, or concrete dependencies.

## 25. Feasibility references

- Krita Linux command-line manual: <https://docs.krita.org/en/reference_manual/linux_command_line.html>
- Krita file menu and Sessions manager: <https://docs.krita.org/en/reference_manual/main_menu/file_menu.html>
- Visual Studio Code command-line interface: <https://code.visualstudio.com/docs/configure/command-line>
- Visual Studio Code profiles: <https://code.visualstudio.com/docs/configure/profiles>
- XDG Desktop Portal documentation: <https://flatpak.github.io/xdg-desktop-portal/docs/>
- XDG Desktop Portal backend guidance: <https://flatpak.github.io/xdg-desktop-portal/docs/writing-a-new-backend.html>
