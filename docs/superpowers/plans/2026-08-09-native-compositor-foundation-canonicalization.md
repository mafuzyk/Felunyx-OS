# Native Compositor Foundation Canonicalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Canonicalize the approved native compositor strategy without beginning Phase 8 implementation.

**Architecture:** Preserve the existing Rust + Smithay technology lineage while superseding the assumption that Felunyx must build directly from bare Smithay. Record mature compositor derivation as the accepted strategy, `pop-os/cosmic-comp` as the provisional first prototype foundation, and an explicit decoupling/upstream-sync gate before long-term adoption.

**Tech Stack:** Markdown architecture documents, GitHub review workflow, upstream `pop-os/cosmic-comp` source evidence.

## Global Constraints

- Phase 2 remains active; this work must not modify the ISO, installer, boot path, packages, workflows, or Phase 2 validation.
- The native desktop remains outside the first usable release critical path.
- Do not invent final crates, D-Bus interfaces, databases, protocols, or dependency pins.
- Preserve Qt 6/QML for presentation and Rust for state, policy, validation, and privileged behavior.
- Preserve history: D-020 must become `Superseded`, not be deleted.
- `cosmic-comp` is provisional until Phase 8 proves decoupling, compatibility, shell replacement, and sustainable upstream synchronization.

---

### Task 1: Canonical decision register

**Files:**
- Modify: `DECISIONS.md`

**Interfaces:**
- Consumes: approved design in `docs/superpowers/specs/2026-08-09-native-compositor-foundation-design.md`.
- Produces: canonical decision IDs referenced by architecture and roadmap documents.

- [ ] **Step 1: Supersede D-020**

Change D-020 from `Accepted` to `Superseded` and state that it is replaced by the new compositor-foundation decisions.

- [ ] **Step 2: Add accepted mature-foundation decision**

Add an accepted decision stating that the native compositor derives from a mature Wayland compositor foundation and keeps low-level infrastructure upstream-derived where sustainable, while Felunyx owns compositor policy and shell behavior.

- [ ] **Step 3: Add provisional COSMIC decision**

Add a provisional decision naming `pop-os/cosmic-comp` as the preferred first Phase 8 foundation, conditional on decoupling, compatibility, and upstream-sync gates.

- [ ] **Step 4: Re-read decision ordering**

Verify no existing accepted entry still requires a bare-Smithay implementation and that the new decision IDs do not collide with existing IDs.

- [ ] **Step 5: Commit**

Use a focused `docs:` commit covering the decision-register change.

### Task 2: Canonical architecture and roadmap

**Files:**
- Modify: `ARCHITECTURE.md`
- Modify: `docs/architecture/felunyx-desktop.md`
- Modify: `ROADMAP.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: the new decision IDs from Task 1.
- Produces: consistent public architecture language and Phase 8 validation gates.

- [ ] **Step 1: Update architecture summary**

Replace claims that the native compositor is simply “built in Rust on Smithay” with language that it is Rust/Smithay-lineage, derived from a mature compositor foundation when validated, with `cosmic-comp` the provisional first prototype foundation.

- [ ] **Step 2: Add ownership boundary**

In `ARCHITECTURE.md` and `docs/architecture/felunyx-desktop.md`, distinguish upstream-derived low-level compositor infrastructure from Felunyx-owned workspace, layout, stack, focus, restoration, rules, Work Environment, and shell policy.

- [ ] **Step 3: Add decoupling and maintenance gates**

State that COSMIC-specific configuration/services/presentation are not automatically adopted, and that the prototype must prove a sustainable delta and upstream synchronization path.

- [ ] **Step 4: Update Phase 8 scope and exit criteria**

Make Phase 8 start from a pinned mature compositor baseline, prove nested/TTY operation, minimal Qt/QML shell replacement, a Felunyx-specific layout vertical slice, decoupling inventory, and an upstream-sync exercise before final foundation acceptance.

- [ ] **Step 5: Update README summary**

Keep the public description concise: native desktop remains Wayland-only, Rust/Smithay-lineage, Qt/QML, with a mature compositor foundation rather than a from-scratch compositor.

- [ ] **Step 6: Commit**

Use a focused `docs:` commit covering canonical architecture wording.

### Task 3: Review and integrate

**Files:**
- Review: all files changed by PR #10

**Interfaces:**
- Consumes: Tasks 1–2.
- Produces: reviewed documentation-only PR ready for merge.

- [ ] **Step 1: Inspect PR diff**

Verify the PR changes only documentation and does not touch Phase 2 implementation paths.

- [ ] **Step 2: Scan contradictions and placeholders**

Confirm there is no remaining canonical statement that bare Smithay is mandatory, no `TODO`/`TBD`, and no claim that `cosmic-comp` is already implemented or validated.

- [ ] **Step 3: Verify phase language**

Confirm Phase 2 remains active and Phase 8 remains future prototype work.

- [ ] **Step 4: Merge PR #10**

Merge only after the reviewed head SHA is known and use that SHA as the expected merge head.
