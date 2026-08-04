# Felunyx Calamares integration

Phase 2 packages the upstream framework separately from Felunyx policy. Automatic encrypted installation is deliberately disabled until GRUB, initramfs and recovery are verified together. Erase is never preselected.

Package ownership remains explicit: the `calamares` package owns and installs its desktop entry, while `felunyx-calamares-config` owns only Felunyx configuration and target-install templates. The GRUB template is copied to the target by `unpackfs`; the configuration package never claims `/etc/default/grub`, which remains owned by `grub`.

The virtual installer harness must use an upstream-supported unattended/test interface or stable accessibility object names. Coordinate clicking is forbidden.
