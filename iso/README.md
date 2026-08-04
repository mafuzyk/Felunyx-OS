# Felunyx Phase 2 archiso profile

This is a resolved, committed profile derived from the official `archlinux/archiso` tag `v89` (`archiso 89-1`). The upstream lock records the exact blobs used as design baselines. Felunyx intentionally replaces package inventory, identity, both kernel entries, live policy and installer integration.

`pacman.conf` contains exactly one allowed materialization token: `@FELUNYX_REPO_URI@`. `tools/felunyx-build` replaces it inside a temporary profile with the absolute URI of the build-local development repository; the committed profile is never edited during a build.
