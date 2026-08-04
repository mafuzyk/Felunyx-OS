# Contributing to Felunyx OS

Felunyx is in an early, specification-driven stage. Contributions are welcome when they preserve the project’s philosophy, phase boundaries, and architectural decisions.

## Before contributing

Read:

1. [VISION.md](VISION.md)
2. [PHILOSOPHY.md](PHILOSOPHY.md)
3. [ARCHITECTURE.md](ARCHITECTURE.md)
4. [DECISIONS.md](DECISIONS.md)
5. [ROADMAP.md](ROADMAP.md)

A technically valid change can still be inappropriate if it introduces visual imitation, hidden behavior, duplicated platform logic, or maintenance the project cannot justify.

## Phase discipline

Work must belong to the active phase or be clearly isolated research.

Experimental branches may explore later phases, but they must not:

- silently freeze public interfaces;
- be described as shipped capability;
- bypass review gates;
- force unfinished native-desktop work onto the distribution’s critical path.

## Branches

Recommended branch prefixes:

- `agent/` — work produced by an agentic workflow
- `feat/` — user-facing capability
- `fix/` — defect correction
- `docs/` — documentation-only change
- `refactor/` — behavior-preserving restructuring
- `research/` — disposable or exploratory validation

Use a short, descriptive suffix such as `agent/foundation-spec` or `feat/transaction-planner`.

## Commits

Prefer small commits that leave the repository understandable.

Recommended style:

```text
docs: define recovery workflow
feat: add transaction risk model
fix: preserve home snapshot on restore
test: cover interrupted package transaction
refactor: separate source resolution from execution
```

Do not combine unrelated cleanup with a focused feature.

## Pull requests

A pull request should explain:

- what changed;
- why it belongs in the current phase;
- which accepted decisions it implements or changes;
- user and developer impact;
- validation performed;
- failure and rollback behavior;
- documentation updates.

Draft pull requests are preferred while a phase deliverable is still being assembled.

## Architecture changes

Do not quietly contradict [DECISIONS.md](DECISIONS.md).

A decision change must:

1. cite the affected decision ID;
2. explain new evidence or constraints;
3. describe compatibility and migration;
4. update architecture and product documentation;
5. preserve the old entry as Superseded;
6. add validation for the new behavior.

## Design requirements

Official user-facing work must include:

- normal state;
- loading state;
- empty state;
- error state;
- confirmation where consequences matter;
- success or result state;
- keyboard navigation;
- accessible labels and focus;
- behavior with animation disabled;
- behavior with blur/transparency disabled;
- source and scope visibility for system-changing actions.

Mockups alone are not complete product design.

## Implementation requirements

- Prefer focused components with defined interfaces.
- Keep policy and privileged logic out of QML.
- Keep source-specific package truth visible.
- Use atomic writes for critical configuration.
- Design interrupted and offline states.
- Write tests before or with behavior changes.
- Do not add dependencies without explaining ownership, update cadence, security, and packaging impact.
- Do not fork upstream solely to make theming easier.

## Testing expectations

The exact commands evolve by phase, but a change should provide the strongest relevant evidence available:

- formatting and lint checks;
- unit tests;
- contract tests;
- integration tests;
- VM boot tests;
- installer tests;
- snapshot and restore tests;
- accessibility checks;
- manual visual verification;
- failure injection;
- upgrade and migration tests.

A passing happy-path demo is not sufficient for package, installer, boot, storage, privilege, or recovery changes.

## Documentation

Canonical documentation belongs in the repository and changes with behavior.

Do not use:

- undocumented magic values;
- placeholder notes as a substitute for a requirement;
- screenshots as the only explanation;
- instructions that require editing configuration files when an official GUI exists;
- claims that a roadmap item already ships.

## Licensing

By contributing, you agree that your contribution is licensed under the repository’s applicable license. Do not add code, assets, fonts, icons, sounds, or packaging content without compatible licensing and attribution.
