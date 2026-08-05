# Phase 2 Virtual Tests

## Scope

These commands exercise the Felunyx OS Phase 2 development image in disposable QEMU guests. They produce structured evidence for review; source validation alone does not establish the Virtual gate.

A matching ISO must be rebuilt after guest-side harness changes. The image from workflow run `30951476281` predates this hardening and cannot validate it.

## Resources

Default scenario resources are:

- 2 virtual CPUs;
- 4 GiB RAM;
- a new 64 GiB QCOW2 disk for each installation scenario;
- QEMU/KVM when `/dev/kvm` is available;
- QEMU TCG fallback otherwise, with longer practical runtime;
- OVMF for required UEFI scenarios;
- SeaBIOS/QEMU default firmware for the best-effort BIOS scenario.

## Evidence model

Every successful or failed runtime scenario owns one artifact directory and writes `scenario-result.json` atomically. The result records `pass`, `fail`, `blocked`, or `not-run`; absence of a record is never success.

Scenario directories may contain:

- `serial.log`;
- `qemu.stderr.log`;
- `qmp-diagnostics.json`;
- a scenario-owned `OVMF_VARS.fd`;
- `loader-entry-oneshot.json`;
- `live-evidence.json`;
- `installed-evidence.json`;
- `grub-next.json`;
- `installer-outcome.json`;
- `guest-evidence.stream`;
- extracted `guest-logs/`.

Installer logs cross the guest boundary through a dedicated virtio-serial port named `org.felunyx.evidence`. The host validates each transported file name, byte count, SHA-256 digest, and Base64 payload before extraction.

## Live UEFI

```bash
tools/felunyx-run-vm boot-live \
  --iso /path/to/Felunyx-OS.iso \
  --kernel zen \
  --artifacts virtual/live-zen \
  --timeout 900

tools/felunyx-run-vm boot-live \
  --iso /path/to/Felunyx-OS.iso \
  --kernel lts \
  --artifacts virtual/live-lts \
  --timeout 900
```

The live kernel is selected through a verified systemd-boot `LoaderEntryOneShot` value in a fresh OVMF variable store. No timed menu input is used.

## Successful installation and installed boots

```bash
tools/felunyx-run-vm install \
  --iso /path/to/Felunyx-OS.iso \
  --disk virtual/felunyx-success.qcow2 \
  --mode success \
  --artifacts virtual/install \
  --timeout 2400

tools/felunyx-run-vm boot-installed \
  --disk virtual/felunyx-success.qcow2 \
  --kernel zen \
  --prepare-next lts \
  --artifacts virtual/installed-zen \
  --timeout 900

tools/felunyx-run-vm boot-installed \
  --disk virtual/felunyx-success.qcow2 \
  --kernel lts \
  --artifacts virtual/installed-lts \
  --timeout 900
```

The Zen boot validates the installed target and writes one verified GRUB `next_entry` for Linux LTS. The following LTS boot uses the same disk and no menu navigation.

## Controlled installer failure

Use a different, nonexistent disk path:

```bash
tools/felunyx-run-vm install \
  --iso /path/to/Felunyx-OS.iso \
  --disk virtual/felunyx-failure.qcow2 \
  --mode failure \
  --artifacts virtual/failure-injection \
  --timeout 2400
```

This scenario passes only when Calamares reaches the intentional `FelunyxInjectedFailure`, reports no success, and transports both `installer-harness.log` and `calamares-debug.log`. A crash, timeout, unrelated failure, inaccessible UI object, or accidental success fails the scenario.

## BIOS best-effort

```bash
tools/felunyx-run-vm boot-bios \
  --iso /path/to/Felunyx-OS.iso \
  --artifacts virtual/bios \
  --timeout 900
```

BIOS is recorded as pass, fail, blocked, or not-run. It cannot weaken or replace the required UEFI result.

## Explicit branch-local workflow trigger

GitHub manual `workflow_dispatch` requires the workflow file to exist on the default branch. During Phase 2 review, `virtual-smoke.yml` still belongs to the isolated implementation branches, so the workflow also supports a narrow branch-local `push` trigger.

That trigger watches only:

```text
docs/evidence/phase-2-virtual-trigger.json
```

The file is intentionally absent during ordinary development. Creating or changing it is an explicit request to run the Virtual gate and must happen only after Mafu approves the smoke and a matching trusted build exists.

The request format is:

```json
{
  "schema": 1,
  "artifact_run_id": 123456789,
  "expected_source_commit": "0123456789abcdef0123456789abcdef01234567"
}
```

Before creating it:

1. identify the successful trusted build run;
2. inspect its `build-info.json` and copy the exact 40-character `source_commit`;
3. confirm that the artifact contains exactly one ISO and belongs to the intended Phase 2 source;
4. obtain Mafu's explicit authorization to run the Virtual smoke;
5. commit only the reviewed request on `fix/phase-2-virtual-gate-hardening`.

The workflow downloads the named artifact, reads its own Phase 2 build metadata, and fails before QEMU when the observed source commit differs from `expected_source_commit`. The harness itself is checked out from the artifact source commit, while the current branch supplies only the controller and fail-closed aggregator.

Do not create the request merely to test the trigger. Keep it until the branch-local trigger is removed or integrated; deleting the watched file is itself a matching push event and would create a noisy failed run.

After the workflow is available on the default branch, normal `workflow_dispatch` with an explicit artifact run ID becomes the preferred entry point.

## Claims and limits

Passing repository tests establishes Remote evidence for source contracts only. A Virtual claim additionally requires:

1. a trusted ISO built from the same source commit;
2. all required scenarios executed;
3. every `scenario-result.json` reviewed;
4. logs, kernel identity, storage layout, bootloader state, and failure evidence inspected;
5. a fail-closed aggregate result.

Hardware remains untested until physical USB, firmware, GPU, network, storage, power, peripheral, and monitor checks are performed separately.
