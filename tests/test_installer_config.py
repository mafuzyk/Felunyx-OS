from pathlib import Path

def read(name): return Path('packages/felunyx-calamares-config',name).read_text()

def test_sequence_has_no_tracking_and_has_summary():
    s=read('settings.conf')
    assert 'tracking' not in s
    assert 'summary' in s
    assert 'partition, mount, unpackfs' in s

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

def test_live_package_removed_and_grub_selected():
    assert 'felunyx-iso-hooks' in read('packages.conf')
    b=read('bootloader.conf')
    assert 'efiBootloader: grub' in b
    assert 'vmlinuz-linux-zen' in b and 'vmlinuz-linux-lts' in b

def test_calamares_source_is_fixed():
    p=Path('packages/calamares/PKGBUILD').read_text()
    assert 'pkgver=3.3.14' in p
    assert '5547f80db067dea923ae693ba6bb88eb2b2eeac1da3ebec42fce453e31c290c0' in p
    assert '6D98B995A1CA6CE4BB906518C7AA337DFA13881E' in p
    assert '-DINSTALL_CONFIG=OFF' in p and '-DWITH_QT6=ON' in p
