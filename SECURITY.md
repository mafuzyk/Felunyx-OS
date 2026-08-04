# Security Policy

## Project maturity

Felunyx OS does not currently publish an installable or supported release. Phase 1 contains specifications and repository policy only.

Security claims begin only when the related implementation, update path, fallback path, and recovery path are tested.

## Reporting a vulnerability

Do not publish exploit details in a normal issue.

Use GitHub private vulnerability reporting when it is available for this repository. When private reporting is unavailable, open a minimal public issue stating that you need a private security contact, without including reproduction details, secrets, personal data, or exploit code.

The project will acknowledge supported reports when active maintainers are available. No response-time guarantee exists before a public release and formal security team are established.

## Security principles

Felunyx is designed around:

- explicit privilege boundaries;
- inspectable transactions;
- signed package and repository metadata;
- risk-based snapshots;
- minimal persistent privileged services;
- local-first data processing;
- no default telemetry;
- no remote access by default;
- consent before diagnostic submission;
- full source identity for installed software;
- recovery that shows proposed commands and effects;
- separate failure domains for compositor, shell, UI, and privileged services.

## Package trust

Managed package operations must retain:

- package source;
- repository or catalog identity;
- version;
- hashes;
- signature status;
- build provenance where available;
- metadata freshness;
- transaction history.

A failed verification blocks the affected managed version. Manual unmanaged installation remains possible through standard Arch tooling, but Felunyx must identify it as outside managed verification.

## Update safety

A security update is not complete merely because it downloads.

The release process must consider:

- dependency effects;
- bootability;
- fallback kernel;
- snapshot scope;
- service restart requirements;
- reboot-pending state;
- rollback;
- repository metadata validity;
- compromised-version blocking;
- key rotation and revocation.

## Recovery security

The recovery environment:

- does not enable remote access by default;
- does not submit reports without consent;
- does not hide commands;
- treats mounted user data carefully;
- avoids storing credentials in exported logs;
- makes destructive storage operations explicit;
- remains useful offline.

## Telemetry and diagnostics

Felunyx has no default telemetry.

Any future diagnostic program requires a separate accepted decision and must be:

- opt-in;
- inspectable before submission;
- limited to declared fields;
- revocable;
- documented with retention and deletion policy;
- independent from essential updates;
- free from advertising or profiling use.

## Supported versions

No supported version exists yet.

When public releases begin, this section will list supported channels, end-of-life policy, security update expectations, and upgrade requirements.
