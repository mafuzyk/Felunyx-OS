# Phase 2 Virtual Gate Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a successful Phase 2 virtual-smoke run prove the required UEFI live, installation, installed-system, storage, fallback-kernel, and retained-failure properties without timing-dependent input or false success.

**Architecture:** Guest-side collectors emit versioned, read-only JSON evidence over serial only when explicit QEMU fw_cfg markers enable testing. Host-side tools select systemd-boot entries through a verified `LoaderEntryOneShot` OVMF variable, launch isolated scenarios, validate strict live or installed schemas, and preserve all evidence. GitHub Actions runs every required scenario independently and a final fail-closed summary determines the Virtual gate result.

**Tech Stack:** Bash 5, Python 3 standard library, systemd/systemd-boot Boot Loader Interface, QEMU, OVMF, `python3-virt-firmware` / `virt-fw-vars` 24.1.1-2 on Ubuntu 24.04, Calamares 3.3.14, AT-SPI, GRUB, Btrfs, pytest, GitHub Actions.

## Global Constraints

- Owning phase is Phase 2; Phase 3 remains blocked.
- Base is `agent/phase-2-implementation` at `1f89d17b10c8e0b4965a7f8ebc5e4d509e5f637a`.
- Linux Zen is the default and Linux LTS is the explicit fallback.
- Required firmware path is UEFI x86_64; BIOS remains best-effort and cannot change the required result.
- GRUB is the only installed bootloader validated in Phase 2.
- Automatic installation uses GPT, a FAT32 ESP at `/boot/efi`, and Btrfs subvolumes `@`, `@home`, `@snapshots`, `@cache`, `@log`, with conditional `@swap`.
- Expected mounts are `/`, `/home`, `/.snapshots`, `/var/cache`, `/var/log`, and `/boot/efi`.
- Btrfs uses `defaults,compress=zstd:1`; EFI uses `defaults,umask=0077`.
- Plasma Wayland must be observed as an active user session; installed files alone are insufficient.
- No coordinate clicking, translated-title matching, timed menu arrows, or silent fallback is allowed.
- Test evidence is opt-in through explicit fw_cfg markers and is not a public API.
- Missing, malformed, skipped, cancelled, blocked, or unrecorded required evidence is never pass.
- Static tests establish only Remote evidence; Virtual remains pending until a matching rebuilt ISO runs successfully and artifacts are reviewed.
- The existing run `30951476281` and its ISO remain unchanged and cannot inherit future validation retroactively.

---

### Task 1: Version and Strengthen Live Evidence

**Files:**
- Modify: `packages/felunyx-identity/felunyx-evidence`
- Modify: `packages/felunyx-identity/felunyx-evidence.service`
- Modify: `tests/boot/expect_serial.py`
- Modify: `tests/test_virtual_harness.py`
- Create: `tests/fixtures/evidence/live-zen-valid.json`
- Create: `tests/fixtures/evidence/live-missing-plasma.json`

**Interfaces:**
- Produces serial line `FELUNYX_EVIDENCE=<json>` with `schema: 2`.
- Produces `collect_sessions() -> list[dict[str, object]]` inside `felunyx-evidence`.
- `expect_serial.py` accepts `--mode live|installed`, `--kernel zen|lts`, and writes the validated payload with `--output PATH`.

- [ ] **Step 1: Write failing strict-schema tests**

Add tests that load fixtures and require rejection when any of these is absent or false in live mode: `uefi`, `graphical_target`, `sddm`, `networkmanager`, `plasma_wayland_available`, or one active local user session whose `type` is `wayland` and whose `desktop` contains `KDE` or `plasma` case-insensitively.

```python
def test_live_evidence_requires_active_plasma_wayland(tmp_path):
    result = run_expect("live-missing-plasma.json", "live", "zen", tmp_path)
    assert result.returncode != 0
    assert "active Plasma Wayland session" in result.stderr
```

- [ ] **Step 2: Run the focused tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k 'live_evidence or plasma'`

Expected: FAIL because schema 1 has no strict mode, active-session evidence, or output file.

- [ ] **Step 3: Implement schema 2 collection**

Collect:

```python
{
    "schema": 2,
    "id": "felunyx",
    "build_metadata": Path("/usr/lib/felunyx/build-info.json").is_file(),
    "kernel": uname,
    "kernel_variant": variant,
    "live": Path("/run/felunyx/live").exists(),
    "uefi": Path("/sys/firmware/efi").is_dir(),
    "graphical_target": active("graphical.target"),
    "sddm": active("sddm.service"),
    "networkmanager": active("NetworkManager.service"),
    "plasma_wayland_available": Path("/usr/share/wayland-sessions/plasma.desktop").is_file(),
    "sessions": collect_sessions(),
    "sshd_service_active": active("sshd.service"),
    "sshd_socket_active": active("sshd.socket"),
}
```

Implement `collect_sessions()` using `loginctl list-sessions --no-legend --no-pager`, then `loginctl show-session ID -p Name -p Class -p Type -p Desktop -p Active -p Remote --value` or individual property calls. A session qualifies only when `Class=user`, `Type=wayland`, `Active=yes`, `Remote=no`, and desktop is KDE/Plasma.

Change the service ordering to:

```ini
After=graphical.target display-manager.service
Wants=display-manager.service
```

The collector may wait up to 120 seconds for the qualifying session, but must emit the final observed state rather than manufacture success.

- [ ] **Step 4: Implement strict host validation**

Refactor `expect_serial.py` into pure validation helpers:

```python
def validate_common(data: dict, kernel: str) -> None: ...
def validate_live(data: dict) -> None: ...
def validate_installed(data: dict) -> None: ...
```

Require schema 2, exact kernel variant, Felunyx identity, build metadata, UEFI, inactive SSH service and socket. Live mode additionally requires the active Plasma Wayland session and active graphical target, SDDM, and NetworkManager. Write canonical sorted JSON atomically to `--output` only after validation succeeds.

- [ ] **Step 5: Run focused and repository tests**

Run:

```bash
python3 -m pytest -q tests/test_virtual_harness.py
python3 -m pytest -q
make lint
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add packages/felunyx-identity tests/boot/expect_serial.py tests/test_virtual_harness.py tests/fixtures/evidence
git commit -m "test: require active Plasma live evidence"
```

---

### Task 2: Select Live Kernels Through Verified OVMF Variables

**Files:**
- Create: `tests/boot/set_loader_oneshot.py`
- Create: `tests/fixtures/ovmf/loader-entry-oneshot.json`
- Modify: `tools/felunyx-run-vm`
- Modify: `tests/test_virtual_harness.py`
- Modify: `.github/workflows/virtual-smoke.yml`

**Interfaces:**
- `set_loader_oneshot.py --vars PATH --entry ENTRY --report PATH` modifies one scenario-owned OVMF vars copy in place and emits a JSON report.
- Allowed entries are exactly `felunyx-linux-zen.conf` and `felunyx-linux-lts.conf`.
- Report fields: `schema`, `tool`, `tool_version`, `guid`, `variable`, `entry`, `verified`.

- [ ] **Step 1: Write failing helper-contract tests**

Require rejection of unknown entries, missing varstores, missing `virt-fw-vars`, failed command status, output without `LoaderEntryOneShot`, and readback whose UTF-16LE value differs from the requested entry.

```python
def test_loader_oneshot_rejects_positional_fallback():
    text = Path("tools/felunyx-run-vm").read_text()
    assert "qmp_sendkey.py" not in text
    assert "sleep 2" not in text
    assert " down ret" not in text
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k oneshot`

Expected: FAIL because the current harness uses timed QMP keys.

- [ ] **Step 3: Implement the variable helper**

Use vendor GUID `4a67b082-0a4c-41cf-b6c7-440b29bb8c4f`, variable name `LoaderEntryOneShot`, attributes `NV|BS|RT` (`7`), and UTF-16LE NUL-terminated entry data. Use the installed `virt-fw-vars` JSON import/export path:

```python
payload = {
    "version": 2,
    "variables": [{
        "name": "LoaderEntryOneShot",
        "guid": SYSTEMD_BOOT_GUID,
        "attr": 7,
        "data": base64.b64encode((entry + "\0").encode("utf-16-le")).decode("ascii"),
    }],
}
```

Write the payload atomically, run `virt-fw-vars --input VARS --set-json PAYLOAD --output TEMP`, replace the scenario vars file only after success, then run `virt-fw-vars --input VARS --output-json READBACK`. Parse the readback, decode the matching variable, and require exact equality. Record the installed tool version. If Ubuntu 24.04's output uses the same fields under a wrapper object, normalize only that documented wrapper; do not guess alternate field names or fall back to input keys.

- [ ] **Step 4: Integrate before QEMU launch**

In `felunyx-run-vm`, make a fresh vars copy for every scenario. For each `boot-live` invocation call:

```bash
python3 "$ROOT/tests/boot/set_loader_oneshot.py" \
  --vars "$vars" \
  --entry "felunyx-linux-${kernel}.conf" \
  --report "$artifacts/loader-entry-oneshot.json"
```

Abort before QEMU if the report is not verified. Remove the QMP key-selection path; retain QMP only for diagnostics and controlled shutdown.

- [ ] **Step 5: Pin executor dependency**

Add `python3-virt-firmware` to the Ubuntu 24.04 install step and assert `virt-fw-vars --version` or package version is recorded before scenarios run.

- [ ] **Step 6: Run tests**

Run:

```bash
python3 -m pytest -q tests/test_virtual_harness.py
python3 -m pytest -q tests/test_workflows.py
make validate
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add tests/boot/set_loader_oneshot.py tests/fixtures/ovmf tools/felunyx-run-vm tests/test_virtual_harness.py .github/workflows/virtual-smoke.yml
git commit -m "test: select live kernels through OVMF one-shot entries"
```

---

### Task 3: Add Installed-System Evidence and Assertions

**Files:**
- Create: `packages/felunyx-identity/felunyx-installed-evidence`
- Modify: `packages/felunyx-identity/PKGBUILD`
- Create: `tests/boot/assert_installed_system.py`
- Create: `tests/fixtures/evidence/installed-zen-valid.json`
- Create: `tests/fixtures/evidence/installed-wrong-btrfs.json`
- Modify: `tests/test_virtual_harness.py`

**Interfaces:**
- Guest command `/usr/lib/felunyx/felunyx-installed-evidence` emits `FELUNYX_INSTALLED=<json>` only when the existing evidence fw_cfg marker is enabled and `/run/felunyx/live` is absent.
- `assert_installed_system.py --log PATH --kernel zen|lts --output PATH --timeout N` validates and persists parsed evidence.

- [ ] **Step 1: Write failing installed-evidence tests**

Test exact requirements:

```python
EXPECTED_SUBVOLUMES = {
    "/": "/@",
    "/home": "/@home",
    "/.snapshots": "/@snapshots",
    "/var/cache": "/@cache",
    "/var/log": "/@log",
}
```

Require `/boot/efi` to be `vfat`, both `linux-zen` and `linux-lts` packages and images, `grub` package, non-empty `/boot/grub/grub.cfg`, `felunyx-iso-hooks` absent, `/run/felunyx/live` absent, `/etc/sudoers.d/10-felunyx-live` absent, `/etc/sddm.conf.d/10-felunyx-live.conf` absent, SSH service/socket inactive, and build metadata present. Btrfs options must include `compress=zstd:1`; EFI options must include `umask=0077` or the equivalent normalized mask.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k installed`

Expected: FAIL because no installed inspector exists.

- [ ] **Step 3: Implement the read-only guest inspector**

Use `subprocess.run(..., check=False, text=True, capture_output=True)` for `pacman -Q`, `findmnt --json --output TARGET,SOURCE,FSTYPE,OPTIONS`, `btrfs subvolume list /`, and systemd states. Never install, enable, repair, regenerate GRUB, or remount. Include command return codes and normalized observations in schema 1 installed payload.

Package the executable as mode `0755` in `felunyx-identity`; it belongs in both live and installed roots, but returns without emitting installed evidence while the live marker exists.

- [ ] **Step 4: Implement strict host assertions**

Parse only `FELUNYX_INSTALLED=`. Reject duplicate success payloads, unknown schema, wrong kernel, wrong mount source, missing subvolume, missing option, live-only residue, or absent boot payload. Persist canonical JSON atomically only after validation.

- [ ] **Step 5: Run tests**

Run:

```bash
python3 -m pytest -q tests/test_virtual_harness.py
python3 -m pytest -q tests/test_identity.py
make validate
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add packages/felunyx-identity tests/boot/assert_installed_system.py tests/fixtures/evidence tests/test_virtual_harness.py
git commit -m "test: inspect installed GRUB and Btrfs state"
```

---

### Task 4: Add Deterministic Calamares Failure Injection

**Files:**
- Create: `packages/felunyx-iso-hooks/calamares-failure/settings.conf`
- Create: `packages/felunyx-iso-hooks/calamares-failure/modules/felunyx-fail/module.desc`
- Create: `packages/felunyx-iso-hooks/calamares-failure/modules/felunyx-fail/main.py`
- Modify: `packages/felunyx-iso-hooks/PKGBUILD`
- Modify: `packages/felunyx-iso-hooks/drive-installation.py`
- Modify: `tests/test_virtual_harness.py`

**Interfaces:**
- fw_cfg marker `opt/felunyx/install-mode` has exact values `success` or `failure`.
- Installer driver emits `FELUNYX_INSTALL=` events: `start`, `stage`, `success`, `failure`, or `blocked`.
- Failure module returns a deterministic Calamares job error class `FelunyxInjectedFailure` after target context exists and before `umount`/success.

- [ ] **Step 1: Write failing configuration and event tests**

Require failure settings to copy the production show/exec sequence but insert `felunyx-fail` after `bootloader` and before `umount`. Require the module to return a structured failure rather than raise an unclassified exception. Require the normal path to remain byte-for-byte governed by production settings.

```python
def test_failure_module_is_explicit_and_cannot_run_normally():
    driver = Path("packages/felunyx-iso-hooks/drive-installation.py").read_text()
    assert "opt/felunyx/install-mode" in driver
    assert "FelunyxInjectedFailure" in Path(
        "packages/felunyx-iso-hooks/calamares-failure/modules/felunyx-fail/main.py"
    ).read_text()
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k failure`

Expected: FAIL because failure injection is absent.

- [ ] **Step 3: Package the test-only overlay**

Install it under `/usr/lib/felunyx/tests/calamares-failure/`, never `/etc/calamares/`. The failure `settings.conf` uses an absolute modules-search path to its test module and `/usr/lib/calamares/modules` for production modules. The PKGBUILD test must prove no test overlay replaces the production config.

- [ ] **Step 4: Strengthen the installer driver**

Read the exact mode from fw_cfg. Launch production Calamares for `success`; launch Calamares with the explicit test settings path for `failure`. Record every event to `/run/felunyx/installer-harness.log` and serial. Preserve `/root/.cache/calamares/session.log`, `/var/log/Calamares.log` when present, and the harness log into `/run/felunyx/installer-evidence/` before powering off.

For failure mode, success is forbidden. Emit:

```python
emit("failure", stage="felunyx-fail", error_class="FelunyxInjectedFailure")
```

only after Calamares reports the expected injected job failure. Any missing accessibility object, crash, timeout, or unexpected result emits `blocked` and exits non-zero.

- [ ] **Step 5: Run tests**

Run:

```bash
python3 -m pytest -q tests/test_virtual_harness.py
python3 -m pytest -q tests/test_installer_config.py
make validate
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add packages/felunyx-iso-hooks tests/test_virtual_harness.py
git commit -m "test: add controlled Calamares failure evidence"
```

---

### Task 5: Refactor the QEMU Harness into Explicit Scenarios

**Files:**
- Modify: `tools/felunyx-run-vm`
- Modify: `tests/test_virtual_harness.py`
- Create: `docs/operations/phase-2-virtual-tests.md`

**Interfaces:**
- Commands:
  - `boot-live --iso ISO --kernel zen|lts --artifacts DIR --timeout N`
  - `install --iso ISO --disk DISK --artifacts DIR --mode success|failure --timeout N`
  - `boot-installed --disk DISK --kernel zen|lts --artifacts DIR --timeout N`
  - `boot-bios --iso ISO --artifacts DIR --timeout N`
- Every command writes `scenario-result.json` with `schema`, `scenario`, `status`, `started_at`, `finished_at`, and `evidence` paths.
- Required status values are `pass`, `fail`, `blocked`, `not-run`.

- [ ] **Step 1: Write failing CLI and artifact tests**

Test invalid argument exit `64`, scenario-owned vars and QMP paths, captured QEMU stderr, no shared OVMF vars, no `|| true` around evidence validators, and atomic `scenario-result.json` creation even on traps.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k 'scenario or cli or artifacts'`

Expected: FAIL because the current script emits only serial logs and suppresses part of installer waiting.

- [ ] **Step 3: Implement common lifecycle helpers**

Add shell functions:

```bash
write_result STATUS MESSAGE
start_qemu
stop_qemu
preserve_diagnostics
```

Redirect QEMU stderr to `$artifacts/qemu.stderr.log`, retain QMP socket diagnostics, copy a fresh OVMF vars file, and use traps that preserve evidence before terminating QEMU. No cleanup may remove the disk or scenario directory.

- [ ] **Step 4: Wire strict validators**

Live scenarios call `expect_serial.py --mode live`. Installed scenarios call `assert_installed_system.py`. Success install requires exactly one `event=success`; failure install requires exactly one expected injected `event=failure`, no success marker, retained logs, and a separate disposable disk.

- [ ] **Step 5: Document exact commands and claims**

Document VM resources (2 vCPU, 4 GiB RAM, 64 GiB disk), KVM/TCG distinction, required new artifact after guest changes, evidence files, manual reproduction commands, and the rule that static validation is not V.

- [ ] **Step 6: Run tests**

Run:

```bash
bash -n tools/felunyx-run-vm
shellcheck tools/felunyx-run-vm
python3 -m pytest -q tests/test_virtual_harness.py
make validate
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add tools/felunyx-run-vm tests/test_virtual_harness.py docs/operations/phase-2-virtual-tests.md
git commit -m "test: make virtual scenarios fail closed"
```

---

### Task 6: Make GitHub Actions Run and Summarize Every Scenario

**Files:**
- Modify: `.github/workflows/virtual-smoke.yml`
- Modify: `tests/test_workflows.py`
- Create: `tests/fixtures/workflows/virtual-gate-summary.json`

**Interfaces:**
- Workflow input remains `artifact_run_id`.
- Scenario step IDs: `live_zen`, `live_lts`, `install`, `installed_zen`, `installed_lts`, `failure_injection`, `bios`.
- Final file: `virtual/gate-summary.json`.

- [ ] **Step 1: Write failing workflow-policy tests**

Require independent named steps, `continue-on-error: true` for evidence continuity, final summary with `if: always()`, explicit required scenario list, BIOS excluded from required aggregate, `python3-virt-firmware` installed, read-only permissions, full-SHA actions, and artifact upload of the whole `virtual/` evidence tree rather than only `*.log`.

```python
REQUIRED = {
    "live_zen", "live_lts", "install",
    "installed_zen", "installed_lts", "failure_injection",
}
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_workflows.py`

Expected: FAIL because scenarios are grouped and no final summary exists.

- [ ] **Step 3: Split workflow execution**

Create the successful installation disk once, then boot it separately for Zen and LTS. Create a different disk for failure injection. Each step writes its result and continues so all possible evidence is collected.

- [ ] **Step 4: Implement fail-closed summary**

Use an inline Python script that reads each required `scenario-result.json`. Missing files become `not-run`. The job exits non-zero unless every required status is `pass`. BIOS is recorded but ignored for required aggregate.

Summary shape:

```json
{
  "schema": 1,
  "required": {
    "live_zen": "pass",
    "live_lts": "pass",
    "install": "pass",
    "installed_zen": "pass",
    "installed_lts": "pass",
    "failure_injection": "pass"
  },
  "best_effort": {"bios": "not-run"},
  "virtual_gate": "pass"
}
```

- [ ] **Step 5: Run policy tests**

Run:

```bash
python3 -m pytest -q tests/test_workflows.py
python3 -m pytest -q
make validate
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/virtual-smoke.yml tests/test_workflows.py tests/fixtures/workflows
git commit -m "ci: summarize every Phase 2 virtual scenario"
```

---

### Task 7: Correct Phase Status Without Promoting Gates

**Files:**
- Modify: `docs/status/phase-2-reproducible-iso.md`
- Modify: `docs/superpowers/specs/2026-08-05-phase-2-virtual-gate-hardening-design.md`
- Modify: `docs/README.md`
- Modify: `tests/test_repository_contract.py`

**Interfaces:** Documentation must expose exact labels: `implemented`, `validated remotely`, `validated in VM`, `validated in hardware`, `pending`, or `not tested`.

- [ ] **Step 1: Write failing documentation-state tests**

Require the status document to mention PR #3, branch and head, build run `30951476281`, development artifact status, R pending review, V pending a matching rebuilt ISO and workflow, H not tested, PR draft, and Phase 3 blocked. Reject the stale phrase `Implementation | Ready to start`.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_repository_contract.py -k phase_status`

Expected: FAIL on stale implementation wording.

- [ ] **Step 3: Update canonical status**

Record:

- implementation exists but is not merged;
- source validation and one trusted frozen build succeeded;
- internal artifact run and digest are evidence inputs, not a release;
- R is pending until all Remote requirements and comparison evidence are reviewed;
- V is pending until the hardened workflow runs against a matching rebuilt ISO and artifacts are reviewed;
- H is not tested and is not required to close Phase 2;
- no merge or Phase 3 before Mafu's phase review.

Change the hardening spec status to `Approved on 2026-08-05; implementation plan written` and link this plan.

- [ ] **Step 4: Run documentation tests**

Run:

```bash
python3 -m pytest -q tests/test_repository_contract.py
make validate
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add docs tests/test_repository_contract.py
git commit -m "docs: record the pending Phase 2 validation gates"
```

---

### Task 8: Verify Source Changes and Prepare the Rebuild Gate

**Files:**
- Modify only when verification exposes a defect in files owned by Tasks 1–7.
- Update: PR #5 description after evidence exists.

**Interfaces:** Produces a source-verification record and an explicit rebuild/Virtual-test handoff; it does not mark V complete.

- [ ] **Step 1: Run the full local Remote suite from a clean checkout**

Run:

```bash
python3 -m pytest -q
make lint
make validate
git diff --check
git status --short
```

Expected: tests pass, no whitespace errors, and only intended tracked changes before the final commit.

- [ ] **Step 2: Audit security and scope**

Run searches requiring no coordinate automation, timed kernel-selection fallback, unpinned action, writable workflow permission, secret/private key, committed ISO, or Phase 3 file:

```bash
! grep -R -nE 'xdotool|pyautogui|moveTo\(|click\(x=|sleep 2.*down.*ret' tools tests packages .github
! grep -R -nE 'uses: [^ ]+@(main|master|v[0-9])' .github/workflows
! grep -R -nE 'contents: write|actions: write' .github/workflows
! find . -type f \( -name '*.iso' -o -name '*.qcow2' -o -name '*.key' -o -name '*.pem' \) -print -quit | grep -q .
```

Expected: every command succeeds; the final `find` negation proves no large image or key was committed.

- [ ] **Step 3: Review the diff against the approved spec**

Confirm every requirement maps to code/tests and no accepted decision changed. Record the strongest achieved level as Remote only.

- [ ] **Step 4: Commit any verification-only corrections**

Use the narrowest applicable prefix, for example:

```bash
git commit -m "fix: preserve complete virtual failure evidence"
```

Skip this commit when no correction is needed.

- [ ] **Step 5: Update draft PR #5**

Add changes, files, decisions, tests, Remote result, Virtual pending state, Hardware not tested, rollback, required new ISO build, and next review point. Keep PR #5 draft and target `agent/phase-2-implementation`.

- [ ] **Step 6: Stop at the implementation review boundary**

Do not merge PR #5 into PR #3, rebuild, dispatch the Virtual workflow, approve Phase 2, or begin Phase 3 without Mafu's next review. After integration approval, build a new matching ISO, run `Virtual Phase 2 smoke`, inspect every scenario artifact, and only then update V evidence.
