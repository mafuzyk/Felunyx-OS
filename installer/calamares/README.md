# Felunyx Calamares integration

Phase 2 packages the upstream framework separately from Felunyx policy. Automatic encrypted installation is deliberately disabled until GRUB, initramfs and recovery are verified together. Erase is never preselected.

The virtual installer harness must use an upstream-supported unattended/test interface or stable accessibility object names. Coordinate clicking is forbidden.

## Package and configuration ownership

Felunyx customizes files at the layer that owns them instead of relying on pacman overwrite flags:

- Arch `filesystem` remains the owner of `/usr/lib/os-release`. `felunyx-identity` owns `/usr/lib/felunyx/os-release` and the higher-priority `/etc/os-release` symlink, so the live and installed systems expose Felunyx identity without replacing the Arch vendor file.
- The Felunyx Calamares recipe remains the sole owner of `/usr/share/applications/calamares.desktop`; its `package()` step installs the Felunyx launcher after the upstream payload is staged.
- Arch `grub` remains the owner of `/etc/default/grub`. `felunyx-calamares-config` owns a template below `/etc/calamares/preinstall_copy/`, and the `unpackfs` sequence copies that template into the target before the bootloader module generates GRUB configuration.

During canonical builds, `tools/felunyx-validate` queries the resolved pacman file databases and fails if `felunyx-identity` or `felunyx-calamares-config` overlaps the corresponding owner package paths.
