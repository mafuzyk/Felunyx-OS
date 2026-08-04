# Sets, Sessions, Rules, Workspaces, and Monitors

## Concepts

### Workspace

A monitor-local organizational space with one primary window mode, optional name, layout, stacks, and configuration overrides.

### Rule

An approved instruction that organizes a matching application after it starts.

### Set

A named temporary working context that may restore workspaces, launch applications, reopen exact application state, and apply scoped preferences.

### Session

The broader state of the user’s desktop, including workspaces, applications, windows, and restorable application content.

These concepts overlap but are not interchangeable.

## Workspaces

### Dynamic lifecycle

Each monitor maintains one trailing empty workspace.

When an application opens there, a new trailing empty workspace appears. Empty intermediate workspaces disappear.

Workspace identity remains stable internally even when visible numbering changes.

### Names and pinning

A workspace can display a number or name.

Naming does not preserve an empty workspace. **Pin workspace** is a separate explicit action.

When an unpinned named workspace disappears, its name may enter a local recent-name list. The user can favorite, remove, or clear recent names.

### Suggestions

Felunyx may suggest names based on:

- current applications;
- application categories;
- active Set;
- local recent names.

Suggestions are local and never applied automatically.

## Monitor ownership

Each monitor has independent:

- workspaces;
- workspace order;
- active workspace;
- overview orientation;
- profile overrides.

Monitor matching uses persistent display identity where available, not only connector name.

### Disconnect

When a monitor disappears:

- its workspaces move temporarily to the primary monitor;
- order, mode, stacks, windows, proportions, and source identity remain;
- the primary overview shows a separate temporary group;
- the workspaces are not mixed into the primary monitor’s normal sequence;
- the user may explicitly adopt a workspace, removing temporary status.

### Reconnect

Default behavior asks whether to restore associated workspaces. A per-monitor automatic option is available.

## Application rules

Rules may match:

- application identity;
- window role/type;
- title or advanced properties;
- current Set;
- monitor presence;
- other explicit conditions.

Rules may set:

- monitor;
- workspace;
- workspace name;
- workspace mode;
- position;
- initial size;
- stack membership;
- focus policy;
- whether a destination workspace is pinned.

An approved rule can create its missing workspace without another prompt.

Rules never launch an application.

### Rule editor

The GUI includes:

- application selector;
- readable conditions;
- destination and organization;
- stack options;
- initial geometry;
- focus behavior;
- priority;
- conflict warnings;
- simulator/preview;
- advanced match properties in a collapsed section.

Regular expressions and text configuration are not required.

Manual rules outrank suggestions. Sets may provide temporary rules.

### Pattern suggestions

Felunyx may locally observe repeated patterns and suggest a rule. It never activates one automatically.

Examples:

- Krita repeatedly moved to Drawing;
- Steam repeatedly moved to the primary monitor;
- Discord repeatedly grouped into one stack.

Suggestion detection can be disabled.

## Sets

A Set may define:

- workspace collection;
- workspace names, pins, and modes;
- applications to launch;
- documents, projects, URLs, and tabs to restore when supported;
- window placement and stacks;
- appearance;
- performance and energy policy;
- notifications and Focus mode;
- audio devices and levels;
- monitor arrangement;
- Bluetooth and network preferences;
- selected services;
- temporary application rules.

### Activation

Default activation preserves the current arrangement and creates or reuses additional Set workspaces. Replacing the current arrangement is an explicit choice in the preview.

Activation is staged:

1. validate referenced applications, workspaces, devices, and services;
2. create or reuse workspaces;
3. apply temporary configuration and device policy;
4. reuse or launch applications;
5. request native application-state restoration;
6. place windows and stacks;
7. validate the resulting Set state.

Activation preview shows:

- workspaces created or reused;
- applications reused or launched;
- application state restored;
- windows moved;
- configuration layers overridden;
- devices or services changed;
- non-restorable items;
- conflicts.

Already-open applications are reused when possible. A new instance is created only when the Set explicitly requires one or the application cannot represent the requested state otherwise.

An already-open application moves only when the preview declares the Set-owned destination. Failed items are summarized once in the Set result rather than producing a storm of independent notifications.

Sets are the only ordinary Felunyx automation that may launch applications.

### Exit

Exiting restores prior temporary settings.

It does not:

- close documents;
- kill applications;
- discard unsaved work;
- delete active workspaces;

without an explicit confirmation.

### Save and update

The user can:

- create a Set from the current state;
- update an existing Set;
- duplicate;
- export;
- inspect imports;
- choose whether activation replaces the current arrangement or opens additional workspaces;
- promote a Set-defined value to Global, Monitor, or Workspace scope.

Advanced scripts may be introduced later only with explicit permission, visible hooks, and import inspection.

## Session restoration

Login policy:

- Ask — default;
- Automatic;
- Never.

Restoration targets exact work state when supported.

### Fidelity order

1. native application session restoration;
2. Felunyx session integration;
3. window-level reopen and placement;
4. explicit non-restorable entry.

Possible state includes:

- documents;
- projects;
- editor tabs;
- browser URLs and profiles through native browser support;
- terminal sessions;
- workspace;
- monitor;
- stack;
- size;
- window state;
- active window;
- tab order.

Felunyx does not scrape or fabricate private application state.

### Sensitive exclusions

Excluded by default:

- password managers;
- banking applications;
- private browsing windows;
- authentication prompts;
- applications marked sensitive;
- secrets displayed in terminals.

Applications can expose a safe restoration contract without exposing content to Felunyx.

## Focus and attention

A new window added to a stack does not steal focus.

When attention is required, the tab receives a restrained activity dot. Applications cannot repeatedly force focus.

Closing the active tab returns to the previously used tab. If no history exists, the nearest tab becomes active.

## Conflict precedence

For declarative configuration:

`Global → Monitor → Workspace → Set → Application`

For immediate behavior, explicit current user action has priority over automation.

The GUI shows:

- winning value;
- source layer;
- overridden values;
- conflict reason;
- restore-inherited action.

A removed rule stops future routing but does not delete a workspace that is currently in use.
