# Installer and First Boot

## Installer goal

The installer should make consequential choices understandable without becoming a decorative slideshow around partitioning tools.

Felunyx uses one deeply customized Calamares ISO.

## Flow

Recommended sequence:

1. language and locale;
2. keyboard;
3. network status;
4. installation destination;
5. partitioning and encryption;
6. bootloader;
7. graphical profile;
8. hardware and driver summary;
9. user and authentication;
10. timezone;
11. complete technical review;
12. installation;
13. result and first-boot guidance.

The exact screen split may change after usability testing, but the review stage remains mandatory.

## Graphical profile

Exactly one profile is selected:

- KDE Plasma — recommended and first available;
- XFCE — available when Phase 6 criteria pass;
- Hyprland — available when Phase 6 criteria pass;
- Felunyx Desktop — only in a channel that accurately reflects its maturity.

The installer explains capability and audience differences without presenting one profile as a benchmark contest.

## Bootloader

- GRUB — default and recommended;
- Limine — official alternative.

Only one is installed.

The review screen shows:

- selected bootloader;
- target disk and EFI partition;
- fallback kernel;
- encryption implications;
- detected existing systems.

## Partitioning

### Automatic

Uses Btrfs and creates distinct system and home scopes.

Options include:

- erase disk;
- install alongside when safely detected;
- encryption;
- swap policy appropriate to memory and hibernation choice.

The exact subvolume naming is frozen during Phase 2 after installation and restore tests.

### Manual

Exposes mount points, filesystems, flags, encryption, and boot requirements.

Felunyx does not rename standard concepts into beginner-friendly metaphors that make external documentation harder to use.

## Encryption

Disk encryption is prominently recommended and remains an explicit choice.

The installer explains:

- what is encrypted;
- what is not encrypted before unlock;
- recovery-key responsibility;
- hibernation implications;
- boot experience;
- data-loss consequences of losing credentials.

## Hardware summary

Before installation, show:

- CPU architecture;
- graphics devices;
- storage target;
- firmware state;
- network hardware;
- selected driver strategy;
- Secure Boot state;
- known limitations detected by current rules.

Hardware detection is evidence, not a promise that every device is fully supported.

## Final review

The review includes:

- disk operations;
- partitions created, deleted, formatted, or resized;
- encryption;
- bootloader;
- kernels;
- desktop profile;
- repositories;
- user;
- locale;
- timezone;
- network requirements;
- proprietary components where applicable.

Destructive actions are visually distinct and described concretely.

## Installation execution

The installer records stage boundaries:

- storage preparation;
- base system;
- kernels and boot;
- repositories and keys;
- profile;
- users;
- services;
- initramfs;
- bootloader;
- validation.

Failure displays the failing stage and allows logs to be saved. A generic “Installation failed” page without evidence is unacceptable.

## First boot

The first boot experience is short and practical.

Possible tasks:

- confirm display arrangement and scaling;
- confirm update policy;
- choose session restoration policy;
- explain snapshots and recovery;
- offer optional account/service connections;
- choose fixed or adaptive accent;
- show where Central and Settings live.

It does not:

- force cloud accounts;
- enable telemetry;
- play a marketing video;
- ask preferences already selected in the installer;
- hide pending hardware warnings.

## Boot visual

Normal boot uses:

- dark background;
- small lynx mark;
- discreet progress;
- logs only when error or explicitly requested;
- no boot sound.

## Login and lock

The first implementation may use greetd with ReGreet while the native greeter matures.

The login surface:

- remembers the last session;
- shows user, password, and session controls;
- remains minimal and quiet;
- matches lock-screen identity.

The lock screen shows clock, date, user, password, and privacy-filtered notifications. Nonessential network, media, and system-state clutter remains hidden.
