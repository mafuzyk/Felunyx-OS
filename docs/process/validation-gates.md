# Validation Gates: Remote, Virtual, and Hardware

Felunyx distinguishes work that can be proven through source and automation from behavior that requires a virtual machine or physical hardware. This prevents absence of evidence from being reported as success while allowing useful work to continue without a local PC.

## Gate R — Remote

Remote validation covers evidence that can be produced through repository review, deterministic tooling, containers, and ordinary CI runners.

Typical evidence:

- specifications, architecture, and source ledgers;
- formatting, schema, static-analysis, and policy checks;
- unit, property, and contract tests;
- package manifests, signatures, checksums, and provenance metadata;
- reproducible build inputs;
- filesystem and image-content inspection without booting;
- mocked or simulated failure fixtures;
- documentation and runbook validation.

Passing R proves that the implementation and its declared inputs are internally consistent. It does not prove that firmware, a graphical session, storage hardware, or a physical device works.

## Gate V — Virtual

Virtual validation covers behavior exercised in an isolated virtual machine or equivalent privileged emulator.

Typical evidence:

- BIOS and UEFI boot;
- live-session startup;
- kernel and fallback-kernel entries;
- virtual disk partitioning and installation;
- Btrfs subvolume creation and mount options;
- installed-system reboot;
- snapshot and rollback exercises;
- package and transaction integration against a disposable system;
- installer failure injection and retained logs;
- basic graphical startup using virtual display hardware.

Passing V proves the declared virtual scenarios. It does not establish physical GPU, firmware, suspend, radio, peripheral, or multi-monitor reliability.

## Gate H — Hardware

Hardware validation covers behavior that depends on physical devices, real firmware, timing, power management, or representative end-user machines.

Typical evidence:

- AMD, Intel, NVIDIA, and hybrid graphics;
- real UEFI implementations and Secure Boot;
- Wi-Fi, Bluetooth, audio, cameras, printers, tablets, and gamepads;
- suspend, resume, hibernation, and low-battery behavior;
- multiple monitors, VRR, HDR, fractional scaling, and hotplug;
- NVMe, SATA, USB storage, dual boot, and encrypted installs;
- touchpads, touchscreens, pens, and input methods;
- performance, heat, battery use, and long-running stability.

Passing H is always scoped to the published hardware matrix. It never implies universal compatibility.

## Phase requirements

Each phase declares which gates are required for completion.

- A phase may require only R, R+V, or R+V+H.
- Evidence is labeled by gate in status documents and pull requests.
- A test passing at one gate must not be described as proof of a stronger gate.
- Unsupported or unavailable gates are recorded as blocked, not silently waived.
- A phase blocked only by V or H may allow isolated preparatory work for the next phase.
- Preparatory work does not mark either phase complete and must not freeze unreviewed public interfaces.

## Claims language

Use precise language:

- **Configured according to source** — static configuration agrees with the cited upstream contract.
- **Validated remotely** — R evidence passed.
- **Booted in a VM** — the named V scenario passed.
- **Validated on hardware** — the named devices and scenarios passed.
- **Not yet validated** — the necessary gate has not been exercised.

Avoid “works,” “supported,” or “stable” without naming the evidence and scope.

## Source-first prevention

When a required gate is unavailable, Felunyx reduces risk by:

1. consulting current primary upstream documentation and source;
2. recording the consulted version, date, decision, and known caveat;
3. validating schemas and generated artifacts statically;
4. comparing with a known upstream reference implementation;
5. creating an executable pending test for V or H;
6. refusing to convert a documented expectation into a completion claim.

## Status format

Phase status documents should contain a table similar to:

| Capability | R | V | H | Evidence or blocker |
|---|---:|---:|---:|---|
| ISO content | Pass | Not required | Not required | Manifest and image inspection |
| UEFI boot | Pass | Pass | Pending | QEMU/OVMF log; physical firmware queue |
| NVIDIA | Pass | Partial | Pending | Package rules only; no physical GPU yet |

A gate is marked Pass only from fresh evidence tied to a commit, artifact, or documented test run.
