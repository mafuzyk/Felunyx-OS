# Public Site Canonicalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile the Felunyx canonical repository so the public website can consume current Phase 2 state and the approved unofficial-desktop policy without inventing exceptions or overriding accepted decisions.

**Architecture:** Keep product authority in `mafuzyk/Felunyx-OS`. Correct the stale Phase 2 status document using only evidence already represented by active draft PRs and add one explicit accepted decision for unofficial desktop/window-manager installs. No implementation, phase transition, interface freeze, or release claim is introduced.

**Tech Stack:** Markdown canonical documents, repository link/format validation, Git diff/static checks.

## Global Constraints

- Base branch is `main`; work stays isolated on `docs/site-public-state-canonicalization` until review.
- Phase 2 remains active and incomplete; do not mark R or V complete without evidence.
- Active Phase 2 implementation remains in draft PRs; this documentation change does not merge or supersede them.
- D-010, D-011, D-012 and D-014 remain accepted.
- New policy: users may install other desktop environments/window managers, but only official profiles receive Felunyx-validated integration, configuration and support.
- “Compatible” must never be used as a synonym for “validated”.
- No public release exists.
- Do not begin Phase 3 implementation.

---

## File Structure

- Modify: `docs/status/phase-2-reproducible-iso.md` — current Phase 2 status/evidence projection.
- Modify: `DECISIONS.md` — add the new accepted unofficial-profile support boundary as D-108.
- No code, workflow, ISO, installer, compositor, package, or Playground files are touched.

---

### Task 1: Reconcile the Phase 2 status document with current draft work

**Files:**
- Modify: `docs/status/phase-2-reproducible-iso.md`

**Interfaces:**
- Consumes: canonical Phase 2 goal/exit criteria from `ROADMAP.md`; active draft PR evidence from PR #3, #5, #8 and #9.
- Produces: a status document that says implementation is active, R is partial/in progress, V is pending, H is not required for Phase 2, and no release/phase-completion claim is made.

- [ ] **Step 1: Record the current evidence boundary before editing**

Verify the document still contains the stale sentence and that the roadmap still declares the Phase 2 goal:

```bash
grep -n "Implementation | Ready to start" docs/status/phase-2-reproducible-iso.md
grep -n "Phase 2 — Reproducible ISO skeleton" ROADMAP.md
```

Expected: the status file still describes implementation as ready to start; the roadmap still identifies Phase 2 as the reproducible ISO skeleton.

- [ ] **Step 2: Replace the stale current-state paragraph**

The opening state must say, in substance:

```text
Design and implementation plan are approved. Phase 2 implementation is active in draft work and remains incomplete. Remote evidence is partial/in progress; Virtual validation is pending a matching rebuilt ISO and runtime evidence; Hardware is not required to close Phase 2.
```

Do not claim that any open draft PR has been integrated into `main`.

- [ ] **Step 3: Replace the implementation row in the evidence table**

Use an explicit status such as:

```markdown
| Implementation | Active — draft, incomplete | PR #3 with hardening/fix work in PR #5, #8 and #9; integration/review pending |
```

Keep the existing specification, source-ledger and plan rows intact unless they are factually stale.

- [ ] **Step 4: Add a short current-work note without duplicating PR bodies**

Add a compact section naming only public status facts:

```markdown
## Current implementation work

- PR #3 contains the Phase 2 reproducible ISO skeleton implementation and remains draft.
- PR #5 hardens the Virtual gate and remains draft.
- PR #8 fixes blockers in the build/Virtual-gate path and remains draft.
- PR #9 addresses the live initrd/microcode boot-path failure and remains draft.

These branches are evidence of active implementation, not evidence that Phase 2 has passed its Remote or Virtual gates.
```

- [ ] **Step 5: Preserve the gate checklists as evidence requirements**

Do not tick boxes merely because source code exists. If any existing box is unchecked on `main`, leave it unchecked unless the canonical repository already contains reviewed evidence proving it.

- [ ] **Step 6: Run focused static validation**

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('docs/status/phase-2-reproducible-iso.md').read_text()
assert 'Ready to start' not in p
assert 'PR #3' in p and 'PR #5' in p and 'PR #8' in p and 'PR #9' in p
assert 'Virtual' in p and 'pending' in p.lower()
assert 'Hardware' in p
assert 'complete and approved' not in p.lower()
PY

git diff --check
```

Expected: PASS.

- [ ] **Step 7: Commit the status reconciliation**

```bash
git add docs/status/phase-2-reproducible-iso.md
git commit -m "docs: reconcile active Phase 2 status"
```

---

### Task 2: Canonicalize the unofficial desktop/window-manager support boundary

**Files:**
- Modify: `DECISIONS.md`

**Interfaces:**
- Consumes: D-010, D-011, D-012 and D-014.
- Produces: accepted D-108, usable by the public FAQ and compatibility documentation.

- [ ] **Step 1: Verify the next decision ID and surrounding desktop decisions**

```bash
grep -n "D-10[0-9]" DECISIONS.md | tail -n 12
grep -n "D-010\|D-011\|D-012\|D-014" DECISIONS.md
```

Expected: D-107 is the highest current ID and the four existing profile decisions remain Accepted.

- [ ] **Step 2: Add D-108 as an Accepted decision**

Add this exact policy meaning to the decision register:

```markdown
| D-108 | Accepted | Felunyx does not prevent users from installing other desktop environments or window managers, but only official profiles receive Felunyx-validated integration, configuration, compatibility guarantees, and project support. Unofficial environments may work, but are outside that validation boundary. |
```

Place it in the desktop-profile/platform domain if practical; if preserving numeric ordering makes that awkward, add it to the later accepted-defaults block and keep the semantic relationship explicit.

- [ ] **Step 3: Add a short compatibility note**

Immediately after the relevant decision block or in the explanatory notes, preserve this public rule:

```text
Compatibility is not the same as validation. An unofficial environment functioning on Felunyx does not imply that Felunyx has tested or supports its integration paths.
```

Do not downgrade or supersede D-010/D-011/D-012/D-014.

- [ ] **Step 4: Validate numbering and wording**

```bash
python3 - <<'PY'
from pathlib import Path
p = Path('DECISIONS.md').read_text()
assert p.count('D-108') == 1
assert 'D-108 | Accepted' in p
for decision in ('D-010', 'D-011', 'D-012', 'D-014'):
    assert f'| {decision} | Accepted |' in p
assert 'only official profiles receive' in p
assert 'validation' in p.lower()
PY

git diff --check
```

Expected: PASS.

- [ ] **Step 5: Commit the decision**

```bash
git add DECISIONS.md
git commit -m "docs: define unofficial desktop support boundary"
```

---

### Task 3: Cross-document review and PR preparation

**Files:**
- Review: `DECISIONS.md`
- Review: `ROADMAP.md`
- Review: `docs/status/phase-2-reproducible-iso.md`

**Interfaces:**
- Produces: a reviewable documentation-only branch with no phase/implementation changes.

- [ ] **Step 1: Check that Phase 2 and profile statements do not contradict the new text**

```bash
python3 - <<'PY'
from pathlib import Path
roadmap = Path('ROADMAP.md').read_text()
decisions = Path('DECISIONS.md').read_text()
status = Path('docs/status/phase-2-reproducible-iso.md').read_text()
assert '**Current state:** complete and approved.' in roadmap  # Phase 1 only
assert 'Phase 2 — Reproducible ISO skeleton' in roadmap
assert 'D-108 | Accepted' in decisions
assert 'Ready to start' not in status
PY
```

If this detects a real contradiction, stop and document it rather than changing unrelated canonical files opportunistically.

- [ ] **Step 2: Review the diff for scope creep**

```bash
git diff main...HEAD -- DECISIONS.md docs/status/phase-2-reproducible-iso.md
git diff --name-only main...HEAD
```

Expected changed files: the plan plus `DECISIONS.md` and `docs/status/phase-2-reproducible-iso.md` only.

- [ ] **Step 3: Run repository-available documentation/static checks**

Run the repository's existing documentation/link/static validation command if present in the checked-out branch, plus:

```bash
git diff --check
```

Do not claim runtime validation; this work is documentation/policy only.

- [ ] **Step 4: Open a draft PR to `main`**

PR summary must state:

```text
Phase: Phase 2 documentation alignment / cross-phase policy clarification
Decisions: adds D-108; does not modify D-010/D-011/D-012/D-014
Validation: R — documentation/static checks only
V/H: not applicable to these documentation changes
Risk: no runtime impact
Rollback: revert the two focused documentation commits
Reason: unblock fail-closed public-site canonical ingestion without teaching the site to ignore known contradictions
```

Do not merge automatically; review the canonical wording before integration.
