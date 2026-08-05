# Agent guidance for Felunyx OS

This file applies to the entire repository. A more specific `AGENTS.md` in a subdirectory may add or override rules for that subtree.

## Mission

Felunyx OS is an Arch-based distribution developed through explicit, gated phases. Preserve its product philosophy, accepted decisions, phase boundaries, and validation model. A technically plausible change is not acceptable if it silently changes product policy, claims unverified behavior, collides with another active branch, or creates maintenance the project has not accepted.

## Read before editing

At minimum, read these files in order:

1. `README.md`
2. `CONTRIBUTING.md`
3. `VISION.md`
4. `PHILOSOPHY.md`
5. `ARCHITECTURE.md`
6. `DECISIONS.md`
7. `ROADMAP.md`
8. the status, design, plan, and operations documents for the task's owning phase

For Phase 2 work, also read:

- `docs/status/phase-2-reproducible-iso.md`
- `docs/superpowers/specs/2026-08-04-phase-2-reproducible-iso-design.md`
- `docs/superpowers/plans/2026-08-04-phase-2-reproducible-iso.md`

Do not treat chat summaries, generated prose, screenshots, or roadmap aspirations as more authoritative than committed canonical documents.

## Mandatory startup inspection

Before proposing or making changes, run and report the relevant results of:

```bash
git status --short --branch
git remote -v
git branch --show-current
git log --oneline --decorate -n 12
```

Then inspect open pull requests and active branches. Verify that the files you intend to edit are not already owned by another active task. Never assume a branch or pull-request description is current merely because it existed in an earlier session.

## Phase and authority rules

- `main` contains canonical accepted work.
- The active implementation phase must be confirmed from committed status documents and current pull requests.
- Later-phase research is allowed only when isolated and clearly labeled as research or preparation.
- Do not implement a later phase without explicit user authorization.
- Do not silently alter an accepted decision. Changes to `DECISIONS.md` must follow the supersession process in `CONTRIBUTING.md`.
- Do not describe Remote evidence as Virtual evidence, or Virtual evidence as Hardware evidence.

## Current coordination snapshot

Snapshot date: **2026-08-05**. Re-check GitHub before relying on this section.

- PR #3, `agent/phase-2-implementation` → `main`: Phase 2 implementation. It is a draft and must not be merged until its Remote and Virtual gates are reviewed and explicitly approved.
- PR #5, `fix/phase-2-virtual-gate-hardening` → `agent/phase-2-implementation`: Phase 2 virtual-gate hardening. It is a child branch of PR #3, not an independent change for `main`.
- PR #6, `docs/work-environments-design` → `main`: documentation-only preparation for Work Environments. It does not authorize Phase 3 implementation and must not be used to modify PR #3 or PR #5.

When this snapshot differs from current GitHub state, current GitHub state and explicit user instructions win. Update this section in a focused documentation pull request when coordination materially changes.

## Branch and pull-request discipline

- Never develop directly on `main`.
- Create a focused branch from the correct base branch.
- Use the branch prefixes documented in `CONTRIBUTING.md`.
- Do not force-push, rewrite shared history, delete branches, retarget pull requests, mark drafts ready, or merge pull requests unless the user explicitly requests that exact action.
- Prefer draft pull requests while work is incomplete.
- Keep commits small, focused, and reviewable.
- Do not mix unrelated cleanup with the requested task.
- If another branch owns a file, stop and coordinate rather than editing through the collision.

## Implementation boundaries

- Keep policy and privileged logic out of QML.
- Prefer small components with explicit interfaces.
- Use atomic writes for critical configuration.
- Explain every new dependency's ownership, update cadence, security impact, and packaging path.
- Do not fork upstream merely to make theming easier.
- Do not invent upstream APIs, schemas, command-line flags, package names, or support claims.
- Preserve source-specific package truth and provenance.
- Design interrupted, offline, partial-success, and rollback behavior where relevant.

## Validation rules

Use the strongest relevant evidence available, but label it honestly:

- **R — Remote:** source review, formatting, lint, unit and contract tests, repository validation, CI logs, manifests, hashes, and artifacts.
- **V — Virtual:** boot, installation, reboot, recovery, desktop session, storage, and integration evidence from disposable virtual machines.
- **H — Hardware:** evidence from physical firmware, graphics, storage, networking, displays, peripherals, suspend, and long-running use.

A weaker gate never implies a stronger one. Missing evidence is not success.

Before claiming completion:

1. run the task's documented validation commands;
2. report exact commands and outcomes;
3. state what was not run and why;
4. inspect the final diff;
5. confirm no unrelated files changed;
6. stop at the owning phase's review boundary.

## Mobile and remote execution

Development may occur from an ARM64 Arch userland under Termux/PRoot. In that environment:

- editing, Git operations, documentation, source analysis, unit tests, and architecture-independent checks are valid when they actually run;
- local `mkarchiso`, privileged mounts, systemd boot behavior, x86_64 execution, UEFI boot, and installer behavior must not be claimed from the PRoot environment;
- use the repository's GitHub Actions workflows for trusted builds and virtual evidence;
- do not weaken workflows, security boundaries, or tests merely to accommodate the mobile environment.

## Security and secrets

- Never commit tokens, credentials, private keys, production signing keys, personal paths, or copied authentication material.
- Do not print secrets into logs.
- Keep workflow permissions minimal and pin third-party actions as required by project policy.
- Treat installer, boot, storage, package, privilege, update, and recovery changes as high-risk.
- Stop and ask before performing destructive operations or changing trust boundaries.

## Expected working style

For non-trivial work:

1. inspect the repository and current coordination state;
2. summarize the relevant constraints;
3. present a focused plan before editing;
4. implement one independently reviewable unit at a time;
5. validate after each unit;
6. commit with a focused conventional message;
7. open or update a draft pull request with validation and rollback notes;
8. stop before merge unless explicitly instructed.

When uncertain, do not guess. Show the ambiguity, cite the conflicting sources, and ask for the smallest decision needed to continue.
