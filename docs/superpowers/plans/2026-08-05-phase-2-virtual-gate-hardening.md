# Phase 2 Virtual Gate Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a successful Phase 2 virtual-smoke run prove the required UEFI live, installation, installed-system, storage, fallback-kernel, and retained-failure properties without timing-dependent input or false success.

**Architecture:** Guest-side collectors emit versioned, read-only JSON evidence over serial only when explicit QEMU fw_cfg markers enable testing. Host-side tools select live systemd-boot entries through a verified `LoaderEntryOneShot` OVMF variable. The installed Zen boot validates the target and may prepare one explicit GRUB one-shot LTS boot through a verified menu-entry ID. GitHub Actions runs every required scenario independently and a final fail-closed summary determines the Virtual gate result.

**Tech Stack:** Bash 5, Python 3 standard library, systemd/systemd-boot Boot Loader Interface, QEMU, OVMF, `python3-virt-firmware` / `virt-fw-vars` 24.1.1-2 on Ubuntu 24.04, GRUB, Calamares 3.3.14, AT-SPI, Btrfs, pytest, GitHub Actions.

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
- No coordinate clicking, translated-title matching, menu-index matching, timed menu arrows, or silent fallback is allowed.
- Test evidence and one-shot preparation are opt-in through explicit fw_cfg markers and are not public APIs.
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
- Produces serial line `FELUNYX_EVIDENCE=<json>` with `schema: 2` only when `/run/felunyx/live` exists.
- `expect_serial.py --log PATH --kernel zen|lts --output PATH --timeout N` validates live evidence and writes canonical JSON atomically.

- [ ] **Step 1: Write failing strict-schema tests**

Add a helper that feeds fixture lines to `expect_serial.py`. Require rejection when any of these is absent or false: `uefi`, `graphical_target`, `sddm`, `networkmanager`, `plasma_wayland_available`, or an active local Plasma Wayland session.

```python
def test_live_evidence_requires_active_plasma_wayland(tmp_path):
    result = run_live_fixture("live-missing-plasma.json", "zen", tmp_path)
    assert result.returncode != 0
    assert "active Plasma Wayland session" in result.stderr
```

- [ ] **Step 2: Run the focused tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k 'live_evidence or plasma'`

Expected: FAIL because schema 1 has no active-session evidence or output file.

- [ ] **Step 3: Implement schema 2 collection**

The emitted object must have exactly these required properties:

```python
required = {
    "schema": 2,
    "id": "felunyx",
    "build_metadata": Path("/usr/lib/felunyx/build-info.json").is_file(),
    "kernel": subprocess.check_output(["uname", "-r"], text=True).strip(),
    "kernel_variant": kernel_variant,
    "live": True,
    "uefi": Path("/sys/firmware/efi").is_dir(),
    "graphical_target": active("graphical.target"),
    "sddm": active("sddm.service"),
    "networkmanager": active("NetworkManager.service"),
    "plasma_wayland_available": Path("/usr/share/wayland-sessions/plasma.desktop").is_file(),
    "sessions": sessions,
    "sshd_service_active": active("sshd.service"),
    "sshd_socket_active": active("sshd.socket"),
}
```

Build `sessions` by listing session IDs with `loginctl list-sessions --no-legend --no-pager`, then querying `Name`, `Class`, `Type`, `Desktop`, `Active`, and `Remote` with one `loginctl show-session` call per session. A qualifying session has `Class=user`, `Type=wayland`, `Active=yes`, `Remote=no`, and `Desktop` containing `KDE` or `plasma` case-insensitively.

Change service ordering to:

```ini
After=graphical.target display-manager.service
Wants=display-manager.service
```

Wait at most 120 seconds for a qualifying session. On timeout, emit the final observed state; do not replace false fields with true values.

- [ ] **Step 4: Implement strict host validation**

Use concrete validation helpers:

```python
def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_live(data: dict, kernel: str) -> None:
    require(data.get("schema") == 2, "live evidence schema must be 2")
    require(data.get("id") == "felunyx", "guest identity is not Felunyx")
    require(data.get("kernel_variant") == kernel, "wrong live kernel")
    require(data.get("live") is True, "live marker is absent")
    require(data.get("uefi") is True, "required UEFI boot was not observed")
    require(data.get("build_metadata") is True, "build metadata is absent")
    require(data.get("graphical_target") is True, "graphical target is inactive")
    require(data.get("sddm") is True, "SDDM is inactive")
    require(data.get("networkmanager") is True, "NetworkManager is inactive")
    require(data.get("plasma_wayland_available") is True, "Plasma Wayland definition is absent")
    require(has_active_plasma_session(data.get("sessions", [])), "active Plasma Wayland session is absent")
    require(data.get("sshd_service_active") is False, "SSH service is active")
    require(data.get("sshd_socket_active") is False, "SSH socket is active")
```

Reject malformed JSON, duplicate evidence lines, unknown schema, and missing keys. Write canonical sorted JSON to `--output` only after validation succeeds.

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
- `set_loader_oneshot.py --vars PATH --entry ENTRY --report PATH` modifies one scenario-owned OVMF vars copy in place.
- Allowed entries are exactly `felunyx-linux-zen.conf` and `felunyx-linux-lts.conf`.
- Report fields are `schema`, `tool_package`, `tool_version`, `guid`, `variable`, `entry`, and `verified`.

- [ ] **Step 1: Write failing helper-contract tests**

Require rejection of unknown entries, missing varstores, missing `virt-fw-vars`, failed command status, missing readback variable, and readback whose UTF-16LE value differs from the requested entry.

```python
def test_loader_oneshot_removes_positional_fallback():
    text = Path("tools/felunyx-run-vm").read_text()
    assert "qmp_sendkey.py" not in text
    assert "sleep 2" not in text
    assert " down ret" not in text
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k oneshot`

Expected: FAIL because the current harness uses timed QMP keys.

- [ ] **Step 3: Implement the variable helper**

Use vendor GUID `4a67b082-0a4c-41cf-b6c7-440b29bb8c4f`, variable name `LoaderEntryOneShot`, attributes `7` (`NV|BS|RT`), and UTF-16LE NUL-terminated entry data.

```python
payload = {
    "version": 2,
    "variables": [{
        "name": "LoaderEntryOneShot",
        "guid": "4a67b082-0a4c-41cf-b6c7-440b29bb8c4f",
        "attr": 7,
        "data": base64.b64encode((entry + "\0").encode("utf-16-le")).decode("ascii"),
    }],
}
```

Write the payload atomically. Run:

```bash
virt-fw-vars --input "$vars" --set-json "$payload" --output "$temporary_vars"
virt-fw-vars --input "$temporary_vars" --output-json "$readback"
```

Parse the readback using the Ubuntu 24.04 package's exported `version` and `variables` fields. Require an exact matching name and GUID, decode `data`, and compare it to the requested entry. Replace the scenario vars file only after readback succeeds. Record the package version with:

```bash
dpkg-query -W -f='${Version}\n' python3-virt-firmware
```

- [ ] **Step 4: Integrate before QEMU launch**

For every live scenario, copy a fresh OVMF vars template and call:

```bash
python3 "$ROOT/tests/boot/set_loader_oneshot.py" \
  --vars "$vars" \
  --entry "felunyx-linux-${kernel}.conf" \
  --report "$artifacts/loader-entry-oneshot.json"
```

Abort before QEMU unless the report contains `"verified": true`. Remove QMP key selection; retain QMP only for diagnostics and controlled shutdown.

- [ ] **Step 5: Pin the executor dependency**

Install `python3-virt-firmware` in the Ubuntu 24.04 workflow step and record its package version into `virtual/executor-packages.txt`.

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
- Modify: `packages/felunyx-identity/felunyx-evidence.service`
- Modify: `packages/felunyx-identity/PKGBUILD`
- Create: `tests/boot/assert_installed_system.py`
- Create: `tests/fixtures/evidence/installed-zen-valid.json`
- Create: `tests/fixtures/evidence/installed-wrong-btrfs.json`
- Modify: `tests/test_virtual_harness.py`

**Interfaces:**
- Guest command `/usr/lib/felunyx/felunyx-installed-evidence` emits `FELUNYX_INSTALLED=<json>` only when the evidence fw_cfg marker is enabled and `/run/felunyx/live` is absent.
- `assert_installed_system.py --log PATH --kernel zen|lts --output PATH --timeout N` validates and persists parsed evidence.

- [ ] **Step 1: Write failing installed-evidence tests**

Use this exact mapping:

```python
EXPECTED_SUBVOLUMES = {
    "/": "/@",
    "/home": "/@home",
    "/.snapshots": "/@snapshots",
    "/var/cache": "/@cache",
    "/var/log": "/@log",
}
```

Require `/boot/efi` to be `vfat`, both `linux-zen` and `linux-lts` packages and images, the `grub` package, non-empty `/boot/grub/grub.cfg`, `felunyx-iso-hooks` absent, live marker absent, live sudo policy absent, live SDDM autologin absent, SSH service/socket inactive, and build metadata present. Btrfs options include `compress=zstd:1`; EFI options include normalized `umask=0077`.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k installed`

Expected: FAIL because no installed inspector exists.

- [ ] **Step 3: Implement the read-only guest inspector**

Use a concrete command helper:

```python
def run(command: list[str]) -> dict:
    completed = subprocess.run(command, check=False, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
```

Collect `pacman -Q`, `findmnt --json --output TARGET,SOURCE,FSTYPE,OPTIONS`, `btrfs subvolume list /`, `/etc/fstab`, GRUB files, kernel files, build metadata, live-only file absence, and systemd states. Never install, enable, repair, regenerate GRUB, remount, or modify configuration.

Package the executable as mode `0755`. Change the oneshot service to run both guarded collectors in order:

```ini
ExecStart=/usr/lib/felunyx/felunyx-evidence
ExecStart=/usr/lib/felunyx/felunyx-installed-evidence
```

The live collector exits silently when the live marker is absent. The installed collector exits silently when the live marker exists.

- [ ] **Step 4: Implement strict host assertions**

Parse only `FELUNYX_INSTALLED=`. Reject duplicate payloads, unknown schema, wrong kernel, wrong mount source, missing subvolume, missing option, live-only residue, active SSH, or absent boot payload. Persist canonical JSON atomically only after validation.

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

### Task 4: Select Installed LTS Through a Verified GRUB One-Shot Entry

**Files:**
- Create: `packages/felunyx-identity/felunyx-prepare-grub-oneshot`
- Modify: `packages/felunyx-identity/felunyx-evidence.service`
- Modify: `packages/felunyx-identity/PKGBUILD`
- Create: `tests/boot/assert_grub_oneshot.py`
- Create: `tests/fixtures/grub/grub.cfg`
- Modify: `tools/felunyx-run-vm`
- Modify: `tests/test_virtual_harness.py`

**Interfaces:**
- fw_cfg `opt/felunyx/grub-next` accepts only `linux-lts`.
- Guest emits `FELUNYX_GRUB_NEXT=<json>` after `grub-reboot` and `grub-editenv` readback succeed.
- `boot-installed` accepts optional `--prepare-next lts` only with `--kernel zen`.

- [ ] **Step 1: Write failing GRUB-selection tests**

The fixture contains a Zen top-level entry and an LTS entry inside the advanced submenu. Test that the parser returns a selector formed only from GRUB IDs:

```python
assert selector == "gnulinux-advanced-ROOTUUID>gnulinux-linux-lts-advanced-ROOTUUID"
```

Reject numeric indexes, display titles, missing `--id`, multiple LTS matches, and entries whose body does not load `vmlinuz-linux-lts`.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k grub_oneshot`

Expected: FAIL because installed LTS currently relies on generic menu input.

- [ ] **Step 3: Implement the guest preparation helper**

The helper exits silently unless the system is installed, the evidence marker is enabled, and `opt/felunyx/grub-next/raw` equals `linux-lts`. Parse `/boot/grub/grub.cfg`, extract the enclosing submenu ID and LTS menuentry ID, and build `submenu_id>entry_id`.

Run:

```bash
grub-reboot "$selector"
grub-editenv /boot/grub/grubenv list
```

Require readback line `next_entry=$selector`. Emit:

```python
{
    "schema": 1,
    "requested": "linux-lts",
    "selector": selector,
    "verified": True,
}
```

Write it to serial as `FELUNYX_GRUB_NEXT=` and to `/run/felunyx/grub-next.json`, call `sync`, then power off. The helper performs no repair and supports no persistent default change.

- [ ] **Step 4: Order the installed boot services**

Add a third oneshot command after installed evidence:

```ini
ExecStart=/usr/lib/felunyx/felunyx-prepare-grub-oneshot
```

This guarantees Zen evidence is emitted before the test-only one-shot preparation powers off.

- [ ] **Step 5: Integrate host validation**

When `boot-installed --kernel zen --prepare-next lts` is requested, add fw_cfg `opt/felunyx/grub-next=linux-lts`, require valid installed Zen evidence, then require valid `FELUNYX_GRUB_NEXT=` evidence. The next ordinary `boot-installed --kernel lts` must reach LTS through GRUB. No QMP navigation is permitted.

- [ ] **Step 6: Run tests**

Run:

```bash
python3 -m pytest -q tests/test_virtual_harness.py
python3 -m pytest -q tests/test_identity.py
make validate
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add packages/felunyx-identity tests/boot/assert_grub_oneshot.py tests/fixtures/grub tools/felunyx-run-vm tests/test_virtual_harness.py
git commit -m "test: select installed LTS through GRUB one-shot state"
```

---

### Task 5: Add Deterministic Calamares Failure Injection

**Files:**
- Create: `packages/felunyx-iso-hooks/calamares-failure-settings.conf`
- Create: `packages/felunyx-iso-hooks/felunyx-fail-module.desc`
- Create: `packages/felunyx-iso-hooks/felunyx-fail-main.py`
- Modify: `packages/felunyx-iso-hooks/PKGBUILD`
- Modify: `packages/felunyx-iso-hooks/drive-installation.py`
- Modify: `tests/test_virtual_harness.py`

**Interfaces:**
- fw_cfg `opt/felunyx/install-mode` has exact values `success` and `failure`.
- Installer events are `start`, `stage`, `success`, `failure`, and `blocked`.
- Failure class is exactly `FelunyxInjectedFailure`.
- makepkg only resolves local package sources by basename in the package directory, so the overlay sources must be flat files beside the PKGBUILD. Their installed target remains below `/usr/lib/felunyx/tests/calamares-failure/`.

- [ ] **Step 1: Write failing configuration and event tests**

Require failure settings to copy the production sequence and insert `felunyx-fail` after `bootloader` and before `umount`. Require the test module to contain:

```python
def run():
    return (
        "FelunyxInjectedFailure",
        "Intentional Phase 2 installer failure injection",
    )
```

Require the normal path to use production settings without copying the failure overlay into `/etc/calamares`.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k failure`

Expected: FAIL because failure injection is absent.

- [ ] **Step 3: Package the test-only overlay**

Install it below `/usr/lib/felunyx/tests/calamares-failure/`. Its `modules-search` contains the absolute test-module directory first and `/usr/lib/calamares/modules` second. Add a package test proving production `/etc/calamares/settings.conf` remains unchanged.

- [ ] **Step 4: Strengthen the installer driver**

Read the exact mode from fw_cfg. Launch production Calamares for `success`; launch Calamares with the explicit failure settings path for `failure`. Record every event in `/run/felunyx/installer-harness.log` and serial. Before poweroff, copy the harness log plus existing Calamares logs into `/run/felunyx/installer-evidence/`.

For failure mode, emit:

```python
emit("failure", stage="felunyx-fail", error_class="FelunyxInjectedFailure")
```

only after the expected Calamares job failure is observed. Unexpected success, timeout, missing accessibility object, crash, or unknown error emits `blocked` and exits non-zero.

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

### Task 6: Refactor the QEMU Harness into Explicit Scenarios

**Files:**
- Modify: `tools/felunyx-run-vm`
- Modify: `tests/test_virtual_harness.py`
- Create: `docs/operations/phase-2-virtual-tests.md`

**Interfaces:**
- `boot-live --iso ISO --kernel zen|lts --artifacts DIR --timeout N`
- `install --iso ISO --disk DISK --artifacts DIR --mode success|failure --timeout N`
- `boot-installed --disk DISK --kernel zen|lts --artifacts DIR [--prepare-next lts] --timeout N`
- `boot-bios --iso ISO --artifacts DIR --timeout N`
- Every command writes `scenario-result.json` with `schema`, `scenario`, `status`, `started_at`, `finished_at`, `message`, and `evidence`.
- Status values are `pass`, `fail`, `blocked`, and `not-run`.

- [ ] **Step 1: Write failing CLI and artifact tests**

Test invalid argument exit `64`, scenario-owned vars and QMP paths, captured QEMU stderr, no shared OVMF vars, no `|| true` around validators, and atomic `scenario-result.json` creation from exit traps.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_virtual_harness.py -k 'scenario or cli or artifacts'`

Expected: FAIL because the current script emits only serial logs and suppresses part of installer waiting.

- [ ] **Step 3: Implement the common lifecycle**

Add these shell functions with one responsibility each:

```bash
write_result(){ python3 "$ROOT/tests/boot/write_scenario_result.py" "$@"; }
start_qemu(){ qemu-system-x86_64 "${args[@]}" 2>"$artifacts/qemu.stderr.log" & pid=$!; }
stop_qemu(){ kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; }
preserve_diagnostics(){ test ! -S "$qmp" || cp -a "$qmp" "$artifacts/qmp.socket.observed" 2>/dev/null || true; }
```

Create `tests/boot/write_scenario_result.py` in this task so JSON is written atomically and shell escaping cannot corrupt it. Traps preserve evidence before terminating QEMU. Cleanup never removes a disk or scenario directory.

- [ ] **Step 4: Wire strict validators**

Live calls `expect_serial.py`. Installed calls `assert_installed_system.py`; Zen preparation also calls `assert_grub_oneshot.py`. Success install requires exactly one success event. Failure install requires exactly one expected failure event, no success event, retained logs, and a separate disposable disk.

- [ ] **Step 5: Document exact commands and claims**

Document 2 vCPU, 4 GiB RAM, 64 GiB disk, KVM/TCG distinction, evidence paths, new-ISO requirement, manual reproduction commands, and that source validation does not establish V.

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
git add tools/felunyx-run-vm tests/boot/write_scenario_result.py tests/test_virtual_harness.py docs/operations/phase-2-virtual-tests.md
git commit -m "test: make virtual scenarios fail closed"
```

---

### Task 7: Make GitHub Actions Run and Summarize Every Scenario

**Files:**
- Modify: `.github/workflows/virtual-smoke.yml`
- Modify: `tests/test_workflows.py`
- Create: `tests/fixtures/workflows/virtual-gate-summary.json`

**Interfaces:**
- Workflow input remains `artifact_run_id`.
- Scenario step IDs are `live_zen`, `live_lts`, `install`, `installed_zen`, `installed_lts`, `failure_injection`, and `bios`.
- Final file is `virtual/gate-summary.json`.

- [ ] **Step 1: Write failing workflow-policy tests**

Require independent named steps, `continue-on-error: true`, final summary with `if: always()`, explicit required scenario list, BIOS excluded from the required aggregate, `python3-virt-firmware` installed, read-only permissions, full-SHA actions, and upload of the complete `virtual/` tree.

```python
REQUIRED = {
    "live_zen",
    "live_lts",
    "install",
    "installed_zen",
    "installed_lts",
    "failure_injection",
}
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_workflows.py`

Expected: FAIL because scenarios are grouped and no final summary exists.

- [ ] **Step 3: Split workflow execution**

Create the successful installation disk once. `installed_zen` validates Zen and prepares the GRUB LTS one-shot. `installed_lts` then boots the same disk without menu input. Create a different disk for failure injection. Every step writes its result and continues so later evidence can be collected.

- [ ] **Step 4: Implement fail-closed summary**

Use inline Python to read each required `scenario-result.json`. Missing files become `not-run`. Exit non-zero unless every required status is `pass`. Record BIOS separately.

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

### Task 8: Correct Phase Status Without Promoting Gates

**Files:**
- Modify: `docs/status/phase-2-reproducible-iso.md`
- Modify: `docs/superpowers/specs/2026-08-05-phase-2-virtual-gate-hardening-design.md`
- Modify: `docs/README.md`
- Modify: `tests/test_repository_contract.py`

**Interfaces:** Documentation uses only `implemented`, `validated remotely`, `validated in VM`, `validated in hardware`, `pending`, and `not tested` for validation state.

- [ ] **Step 1: Write failing documentation-state tests**

Require PR #3, branch and head, build run `30951476281`, artifact digest, internal development status, R pending review, V pending a matching rebuilt ISO and workflow, H not tested, draft state, and Phase 3 blocked. Reject `Implementation | Ready to start`.

- [ ] **Step 2: Run tests and confirm failure**

Run: `python3 -m pytest -q tests/test_repository_contract.py -k phase_status`

Expected: FAIL on stale implementation wording.

- [ ] **Step 3: Update canonical status**

Record that implementation exists but is unmerged; source validation and one trusted frozen build succeeded; the artifact is not a release; R awaits complete evidence and comparison review; V awaits the hardened workflow against a matching rebuilt ISO; H is not tested; and no merge or Phase 3 begins before Mafu's review.

Set the hardening spec status to `Approved on 2026-08-05; implementation plan written` and link this plan.

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

### Task 9: Verify Source Changes and Prepare the Rebuild Gate

**Files:**
- Modify only files owned by Tasks 1–8 when verification exposes a defect.
- Update: draft PR #5 description.

**Interfaces:** Produces a Remote source-verification result and an explicit rebuild handoff. It does not mark V complete.

- [ ] **Step 1: Run the full Remote suite from a clean checkout**

Run:

```bash
python3 -m pytest -q
make lint
make validate
git diff --check
git status --short
```

Expected: tests pass, no whitespace errors, and only intended tracked changes.

- [ ] **Step 2: Audit security and scope**

Run:

```bash
! grep -R -nE 'xdotool|pyautogui|moveTo\(|click\(x=|sleep 2.*down.*ret' tools tests packages .github
! grep -R -nE 'uses: [^ ]+@(main|master|v[0-9])' .github/workflows
! grep -R -nE 'contents: write|actions: write' .github/workflows
! find . -type f \( -name '*.iso' -o -name '*.qcow2' -o -name '*.key' -o -name '*.pem' \) -print -quit | grep -q .
```

Expected: every command succeeds; the final negated pipeline proves no image or key is committed.

- [ ] **Step 3: Review the diff against the approved spec**

Map each specification requirement to code and tests. Confirm no accepted decision changed. Record the strongest achieved level as Remote only.

- [ ] **Step 4: Commit verification corrections only when needed**

Stage only affected files and use the narrowest prefix. Example:

```bash
git add tools/felunyx-run-vm tests/test_virtual_harness.py
git commit -m "fix: preserve complete virtual failure evidence"
```

When no correction is needed, create no empty commit.

- [ ] **Step 5: Update draft PR #5**

Add changes, files, decisions, tests, Remote result, Virtual pending state, Hardware not tested, rollback, required new ISO build, and next review point. Keep PR #5 draft and targeting `agent/phase-2-implementation`.

- [ ] **Step 6: Stop at the implementation review boundary**

Do not merge PR #5 into PR #3, rebuild, dispatch the Virtual workflow, approve Phase 2, or begin Phase 3 without Mafu's next review. After integration approval, build a matching ISO, run `Virtual Phase 2 smoke`, inspect every scenario artifact, and only then update V evidence.
