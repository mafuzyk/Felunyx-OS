# Recovery and Snapshots

## Recovery promise

Felunyx recovery should be usable by someone who does not already know which shell command failed, while remaining honest enough for an expert to inspect and control every action.

It is not a generic wizard that guesses until the machine boots.

## Entry points

Recovery may be entered from:

- a boot failure screen;
- bootloader recovery entry;
- Felunyx Central;
- a snapshot action;
- installation media;
- an explicit recovery command.

The same domain tools should be reused where possible, even when the visual environment differs.

## Boot failure screen

When Felunyx detects a failed or unstable boot, it displays:

- failed component;
- package, mount, unit, kernel, or code when known;
- time of failure;
- likely cause;
- impact;
- available evidence;
- actions.

Primary choices:

- boot Linux LTS;
- select a snapshot;
- inspect and repair;
- open the recovery environment;
- power actions.

The screen does not auto-select after a timeout.

## Recovery visual mode

Recovery retains Felunyx identity but removes unnecessary risk:

- solid or minimally translucent surfaces;
- high contrast;
- no dependency on heavy blur;
- restrained or disabled animation;
- clear focus;
- complete keyboard navigation;
- copy, save, and export for logs;
- a full terminal.

A shell or graphical failure must not make core tools unreachable.

## Categories

### Boot

- kernel and initramfs inspection;
- Linux Zen and Linux LTS state;
- bootloader configuration;
- boot entries;
- failed unit summary;
- rebuild proposals.

### System

- service state;
- authentication;
- configuration migration;
- reboot-pending validation;
- snapshot relationships;
- core package integrity.

### Storage

- mounts;
- Btrfs subvolumes;
- free space;
- filesystem health;
- snapshot storage;
- encrypted-volume state;
- explicit destructive-operation warnings.

### Packages

- package database health;
- interrupted transaction detection;
- repository metadata;
- signature and key state;
- dependency consistency;
- reinstall, complete, or rollback proposals.

### Diagnostics

- hardware summary;
- kernel logs;
- boot logs;
- service logs;
- graphics and input state;
- export with privacy preview.

## Workflow

Every tool follows four stages.

### 1. Analysis

Read-only inspection.

The UI identifies evidence sources and distinguishes facts from inference.

### 2. Proposal

Before changing anything, show:

- exact commands;
- files and mounts affected;
- packages changed;
- expected result;
- snapshot or backup created;
- destructive effects;
- estimated time only when evidence supports it;
- fallback if the proposal fails.

### 3. Confirmation

Confirmation language names the consequence. Dangerous storage actions require stronger confirmation than routine package repair.

### 4. Result

Show:

- commands executed;
- outputs summarized and expandable;
- state changed;
- validation performed;
- remaining warnings;
- next boot or reboot action;
- rollback availability.

## Snapshot scopes

Felunyx recognizes:

- System
- Configuration
- Home
- Full

Automatic transactions generally use System or System + Configuration. Home snapshots are never implied by a system update.

## Automatic snapshot policy

### Smart

Uses risk analysis. Default.

- High risk: snapshot
- Moderate risk: snapshot when specific impact rules match
- Low risk: no automatic snapshot

### Always

Creates an eligible system snapshot before managed system transactions.

### Never

Does not create automatic snapshots. Manual snapshot actions remain available.

## Restore defaults

System restore:

- restores system and relevant configuration;
- preserves current home;
- retains a reference to the pre-restore system state where space allows;
- explains package/source implications.

Home restore:

- first snapshots current home;
- shows files and scope;
- warns about currently open applications;
- avoids silent overwrite where application consistency cannot be guaranteed.

Full restore:

- is explicit;
- never appears as the casual default;
- displays both system and user-data consequences.

## Snapshot lifecycle

Snapshot metadata records:

- creating action;
- risk reasons;
- package transaction;
- creation time;
- scope;
- boot validation state;
- pinned/protected status;
- cleanup eligibility.

A snapshot associated with a kernel, driver, desktop-core, or platform update remains protected until the new state is considered stable.

Cleanup is policy-driven and visible. Felunyx does not silently delete the only known-good recovery state to meet an arbitrary count.

## Network behavior

Networking is available by default in recovery:

- known networks may reconnect;
- new networks request credentials;
- offline tools remain functional;
- remote access is off;
- report submission is off;
- package repair distinguishes cached and network-required actions.

## Privacy

Before exporting diagnostics, Felunyx previews categories and redactions.

Exports should avoid:

- passwords;
- authentication tokens;
- Wi-Fi secrets;
- full personal file paths when not required;
- document content;
- private notification content;
- browser history.

The user chooses where to save or submit the export.

## Failure of recovery itself

When a proposal fails:

- preserve logs;
- do not erase the original evidence;
- show which steps completed;
- avoid repeating destructive steps automatically;
- offer the full terminal;
- permit saving a recovery bundle;
- keep power and alternate-boot actions available.

“No change was made” is stated only when verified.
