import json,re
from pathlib import Path

def packages():
    return {x.strip() for x in Path('iso/profile/packages.x86_64').read_text().splitlines() if x.strip() and not x.startswith('#')}

def test_required_packages_and_no_ssh():
    required={'linux-zen','linux-lts','linux-firmware','amd-ucode','intel-ucode','btrfs-progs','grub','efibootmgr','networkmanager','plasma-meta','plasma-wayland-protocols','sddm','dolphin','konsole','calamares','felunyx-identity','felunyx-iso-hooks','felunyx-calamares-config'}
    assert required <= packages()
    assert 'openssh' not in packages()

def test_profile_identity_and_boot_modes():
    p=Path('iso/profile/profiledef.sh').read_text()
    assert 'iso_name="felunyx-os"' in p
    assert 'install_dir="felunyx"' in p
    assert "'bios.syslinux'" in p and "'uefi.systemd-boot'" in p
    assert len(re.search(r'iso_label="([^"]+)',p).group(1)) <= 32

def test_two_complete_kernel_entries():
    loader=Path('iso/profile/efiboot/loader/loader.conf').read_text()
    assert 'default felunyx-linux-zen.conf' in loader
    for kernel in ('zen','lts'):
        text=Path(f'iso/profile/efiboot/loader/entries/felunyx-linux-{kernel}.conf').read_text()
        assert f'vmlinuz-linux-{kernel}' in text
        assert f'initramfs-linux-{kernel}.img' in text
        preset=Path(f'iso/profile/airootfs/etc/mkinitcpio.d/linux-{kernel}.preset').read_text()
        assert f'vmlinuz-linux-{kernel}' in preset and f'initramfs-linux-{kernel}.img' in preset

def test_upstream_lock_is_exact():
    lock=json.loads(Path('iso/upstream/releng.lock.json').read_text())
    assert lock['archiso_version']=='89-1' and lock['upstream_tag']=='v89'
    assert len(lock['imported_blobs']) >= 10
    assert all(re.fullmatch(r'[0-9a-f]{40}',x) for x in lock['imported_blobs'].values())

def test_only_declared_template_token_exists():
    text=Path('iso/profile/pacman.conf').read_text()
    assert text.count('@FELUNYX_REPO_URI@')==1
