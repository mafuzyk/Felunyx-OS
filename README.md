# Felunyx OS

> **Status:** Phase 1 — foundation and architecture. No installable release exists yet.

Felunyx OS is an Arch-based Linux distribution built around visual authorship, comfort, transparency, reversible change, and a coherent desktop experience.

Its long-term desktop is Wayland-native and built with Rust, Smithay, and Qt/QML. Before that desktop becomes the default, Felunyx will ship a polished reference experience on KDE Plasma and later provide equally intentional XFCE and Hyprland profiles.

**Pronunciation:** *fe-lú-nix*.

## Why Felunyx exists

Linux desktops often force a choice between polished but restrictive, powerful but fragmented, or friendly but technically opaque. Felunyx aims for a different balance:

- beautiful because the system was designed coherently, not because a theme was pasted over it;
- welcoming without hiding packages, services, repositories, or consequences;
- rolling release without treating breakage as a personality trait;
- graphical by default, with a first-class CLI using the same backend;
- customizable without turning every user into the distribution maintainer;
- safe through snapshots, explicit proposals, and understandable recovery—not silent “repair magic.”

The guiding sentence is:

> **Beauty must arise from architecture, not be pasted over.**

## Product pillars

1. **Visual authorship** — Felunyx should be recognizable without imitating Windows, macOS, GNOME, or KDE.
2. **Comfort** — defaults should feel considered, calm, and immediately usable.
3. **Transparency** — important actions expose packages, repositories, commands, files, and effects.
4. **Reversibility** — high-risk changes create deliberate recovery paths.
5. **Control** — the system proposes; the person decides.
6. **Selective ownership** — Felunyx builds what defines its experience and integrates mature upstream work everywhere else.
7. **Privacy** — local-first behavior, no advertising, and no default telemetry.
8. **Consistency** — the GUI, CLI, installer, recovery environment, and desktop profiles share the same concepts.

## Architecture at a glance

- **Base:** Arch Linux, rolling release, `systemd`
- **Filesystems:** Btrfs layout with separated system and home subvolumes
- **Kernels:** Linux Zen by default, Linux LTS installed as fallback
- **Installer:** one deeply customized Calamares ISO
- **Bootloader:** GRUB recommended; Limine available as an explicit alternative
- **Initial reference desktop:** KDE Plasma
- **Additional official profiles:** XFCE and Hyprland after the shared platform stabilizes
- **Future native desktop:** Wayland-only, Rust + Smithay compositor, Qt 6/QML shell and applications
- **System UI:** Felunyx Central, Felunyx Settings, recovery UI, and a shared design system
- **Package sources:** Felunyx repository → Arch repositories → curated AUR → Flatpak → Nix
- **Updates:** unified transactions, risk analysis, targeted snapshots, explicit confirmation
- **Recovery:** analysis → proposal → confirmation → result

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system model and [DECISIONS.md](DECISIONS.md) for accepted decisions.

## Roadmap

Felunyx is developed in gated phases. Work stops at the end of each phase for review before the next begins.

1. Foundation and architecture
2. Reproducible ISO skeleton
3. Core platform and safe transactions
4. KDE reference experience
5. Installer, recovery, and hardware readiness
6. XFCE and Hyprland parity
7. Distribution infrastructure and private alpha
8. Native Felunyx Desktop prototype
9. Public beta
10. Stable 1.0

The detailed gates and deliverables are in [ROADMAP.md](ROADMAP.md).

## Documentation

- [Vision](VISION.md)
- [Philosophy](PHILOSOPHY.md)
- [Architecture](ARCHITECTURE.md)
- [Decision register](DECISIONS.md)
- [Roadmap](ROADMAP.md)
- [Documentation index](docs/README.md)
- [Foundation design specification](docs/superpowers/specs/2026-08-03-felunyx-foundation-design.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## Repository policy

This repository begins as a phased monorepo. It contains the canonical product specification and will later host the ISO definition, distribution packages, platform services, desktop profiles, integration tests, and early native-desktop work.

New top-level implementation directories are created only when their phase begins. Empty architecture cosplay is not a deliverable.

## Project status

Felunyx is an early design and engineering project. Do not use it as an operating system yet, do not treat roadmap items as shipped features, and do not infer release dates from phase numbering.

## License

Unless a file states otherwise, source code in this repository is licensed under the GNU General Public License v3.0. Third-party projects and packaged software retain their own licenses.
