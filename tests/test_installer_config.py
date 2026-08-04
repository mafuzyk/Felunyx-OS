from pathlib import Path

def read(name): return Path('packages/felunyx-calamares-config',name).read_text()

def test_sequence_has_no_tracking_and_generates_initramfs():
    s=read('settings.conf')
    assert 'tracking' not in s
    assert 'summary' in s
    assert 'partition, mount, unpackfs' in s
    assert 'initcpiocfg, initcpio, bootloader' in s

def test_partition_policy_is_safe():
    p=read('partition.conf')
    for value in ('mountPoint: /boot/efi','recommendedSize: 1GiB','minimumSize: 512MiB','initialPartitioningChoice: none','defaultPartitionTableType: gpt','defaultFileSystemType: btrfs'):
        assert value in p
    assert 'enableLuksAutomatedPartitioning: false' in p

def test_btrfs_layout_and_mounts():
    m=read('mount.conf')
    for sub in ('/@','/@home','/@snapshots','/@cache','/@log','/@swap'):
        assert sub in m
    assert 'compress=zstd:1' in m
    assert 'umask=0077' in m

def test_unpackfs_uses_real_archiso_path_and_replaces_live_presets():
    u=read('unpackfs.conf')
    assert '/run/archiso/bootmnt/felunyx/x86_64/airootfs.sfs' in u
    assert '/run/archiso/airootfs' not in u
    assert '/etc/mkinitcpio.d/linux-zen.preset' in u
    assert '/etc/mkinitcpio.d/linux-lts.preset' in u

def test_services_systemd_uses_unit_action_schema():
    s=read('services-systemd.conf')
    assert 'units:' in s
    assert 'enabled:' not in s and 'disabled:' not in s
    for unit in ('NetworkManager.service','sddm.service','qemu-guest-agent.service','sshd.service'):
        assert unit in s

def test_live_package_removed_and_grub_schema_is_real():
    assert 'felunyx-iso-hooks' in read('packages.conf')
    b=read('bootloader.conf')
    assert 'efiBootLoader: "grub"' in b
    assert 'grubInstall: "grub-install"' in b
    assert 'kernel:' not in b and 'fallbackKernel:' not in b
    grub=read('grub-default')
    assert 'GRUB_TOP_LEVEL=/boot/vmlinuz-linux-zen' in grub

def test_calamares_source_is_fixed_and_signed():
    p=Path('packages/calamares/PKGBUILD').read_text()
    assert 'pkgver=3.3.14' in p
    assert '5547f80db067dea923ae693ba6bb88eb2b2eeac1da3ebec42fce453e31c290c0' in p
    assert '1dcf71c518ca9a08f62ad6c6532001c46a72505bac7452e52c567cbd3021a076' in p
    assert "validpgpkeys=('00ACD15E25A79FEE028B0EE57FEA3DA6169C77D6')" in p
    assert 'tar.gz.asc' in p
    assert 'tar.gz.sig' not in p
    assert '-DINSTALL_CONFIG=OFF' in p and '-DWITH_QT6=ON' in p
