# Phase 2 build environment

The canonical environment is the immutable Arch image declared in `environment.lock.json` and `Containerfile`.
It installs packages from one Arch Linux Archive epoch. GitHub Actions is an executor only; repository scripts remain the build interface.

Run preflight before privileged work:

```bash
tools/felunyx-preflight --json artifacts/preflight.json
```

Comparison mode requires enough storage for two independent work trees:

```bash
tools/felunyx-preflight --comparison --json artifacts/preflight.json
```
