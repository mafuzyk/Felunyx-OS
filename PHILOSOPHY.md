# Felunyx OS Philosophy

This document is the decision filter for Felunyx. A feature can be technically impressive and still be wrong for the project if it violates these principles.

## 1. Beauty must arise from architecture

A coherent visual system is the output of coherent components, state, language, and behavior. Felunyx does not solve fragmentation by covering it with a theme.

A feature is visually complete only when its loading, empty, error, confirmation, and recovery states belong to the same design.

## 2. Comfort is not concealment

Felunyx should reduce unnecessary effort without replacing technical truth with vague language.

The system may say “A restart is required,” but it must also say which kernel, driver, desktop component, or service caused that requirement. It may recommend a package source, but it must identify that source and explain why.

Friendly and technical are not opposites.

## 3. The system proposes; the person decides

Felunyx may analyze risk, suggest a layout, detect a repeated pattern, or prepare a recovery action. It does not silently adopt suggestions that alter behavior, transmit information, or modify persistent state.

Approved rules may act automatically within their declared scope. The user’s prior consent is the source of that automation.

## 4. Reversibility is a feature, not a slogan

High-risk operations should create appropriate snapshots. Recovery actions should show commands and effects before execution. Configuration inheritance should make it clear where a value originated and how to return to the inherited state.

Reversibility does not mean snapshotting everything forever. It means matching protection to risk and keeping the recovery model understandable.

## 5. GUI first, CLI equal

Every official end-user capability should have a high-quality graphical path. Configuration files remain available, but no supported feature should require editing one.

The CLI is not a secondary compatibility tool. It uses the same backend, transaction model, validation, and terminology as the GUI.

The GUI must not hide information that the CLI reveals, and the CLI must not bypass safety without an explicit flag.

## 6. Selective ownership

Felunyx owns the components that define its experience:

- platform services and system models;
- Felunyx Central and Settings;
- distribution integration;
- safe transaction and recovery workflows;
- design system and session concepts;
- the future Felunyx Desktop.

It integrates mature upstream components when ownership would add maintenance without adding identity. Forks require a documented reason, tests, and an upstream strategy.

## 7. Integration over forced uniformity

Pacman repositories, AUR packages, Flatpaks, and Nix packages are not the same. Felunyx presents them through one experience while retaining source-specific truth, constraints, and failure modes.

A unified interface must not become a dishonest abstraction.

## 8. Local-first and private by default

Pattern suggestions, recent workspace names, and similar intelligence should operate locally. Telemetry is off by default. Crash reports, diagnostics, remote access, and data transmission require explicit consent.

The lock screen reveals only the notification detail level chosen per application.

## 9. One platform, multiple profiles

KDE Plasma, XFCE, Hyprland, and the future Felunyx Desktop share services, recovery, settings concepts, package behavior, visual tokens, and documentation.

A profile may adapt its interaction model, but it should not invent a separate Felunyx.

## 10. Failure is a first-class state

Felunyx assumes that networks fail, mirrors desynchronize, packages conflict, updates are interrupted, monitors disappear, and graphical shells crash.

Components are separated so that one failure does not unnecessarily destroy the session. The recovery environment is designed alongside the normal system, not after it.

## 11. No repair magic

There is no generic “Fix everything” button.

Recovery follows:

1. analysis;
2. proposal;
3. confirmation;
4. result.

The proposal names commands, files, packages, mounts, and expected effects. Automation is valuable only when the user can understand what it is automating.

## 12. Familiarity without imitation

Felunyx can borrow proven ergonomic patterns: a bottom taskbar, grouped applications, a traditional launcher, window controls on the right, or a calendar opened from the clock.

It must reinterpret those patterns through its own proportions, hierarchy, surfaces, motion, terminology, and workflows. StartAllBack is an ergonomic reference for density and practicality, not a visual specification.

## 13. Defaults are opinions, not prisons

Felunyx chooses strong defaults and explains them. Official settings expose meaningful alternatives without making the default experience look unfinished.

Customization is layered:

`Global → Monitor → Workspace → Set → Application`

More specific layers override earlier ones. The GUI shows the source of the current value and offers “Restore inherited value.”

## 14. Performance includes cognitive performance

Fast boot, low memory use, and responsive animation matter. So do predictable layouts, restrained notifications, stable focus, and avoiding unnecessary prompts.

A technically fast system that constantly interrupts or surprises the user is not fast in practice.

## Decision test

Before accepting a feature, ask:

1. Does it strengthen the Felunyx identity or merely add surface area?
2. Can the user understand what it changes?
3. Is there a complete graphical path?
4. Is its failure state designed?
5. Can it be tested independently?
6. Can it be reversed when appropriate?
7. Does it preserve upstream truth?
8. Does it require a fork, and is that fork justified?
9. Does it behave consistently across official profiles?
10. Would the project still choose it if screenshots were impossible?

A feature that repeatedly fails this test does not belong in Felunyx.
