import json
import os
import subprocess
from pathlib import Path

REQUIRED_PACKAGES={"linux-zen","linux-lts","linux-firmware","amd-ucode","intel-ucode","btrfs-progs","grub","efibootmgr","networkmanager","plasma-meta","plasma-wayland-protocols","sddm","dolphin","konsole","calamares","felunyx-identity","felunyx-iso-hooks","felunyx-calamares-config","mkinitcpio-nfs-utils","nbd"}


def valid_profile(tmp_path:Path):
    profile=tmp_path/'profile'; profile.mkdir()
    (profile/'packages.x86_64').write_text('\n'.join(sorted(REQUIRED_PACKAGES))+'\n')
    (profile/'profiledef.sh').write_text('iso_name="felunyx-os"\ninstall_dir="felunyx"\nbootmodes=("uefi.systemd-boot" "bios.syslinux")\n')
    entries=profile/'efiboot/loader/entries'; entries.mkdir(parents=True)
    (entries/'felunyx-linux-zen.conf').write_text('zen\n')
    (entries/'felunyx-linux-lts.conf').write_text('lts\n')
    (profile/'pacman.conf').write_text('[felunyx]\nServer = file:///tmp/felunyx-repo\n')
    return profile


def fake_pacman(tmp_path:Path,packages:dict[str,list[str]]):
    script=tmp_path/'pacman'
    script.write_text(
        '#!/usr/bin/env python3\n'
        'import json,sys\n'
        f'packages=json.loads({json.dumps(json.dumps(packages))})\n'
        "name=sys.argv[-1]\n"
        "if name not in packages: raise SystemExit(1)\n"
        "print('\\n'.join(packages[name]))\n"
    )
    script.chmod(0o755); return script


def package_lists():
    return {
        'filesystem':['usr/','usr/lib/','usr/lib/os-release'],
        'felunyx-identity':['etc/os-release','usr/lib/felunyx/os-release'],
        'calamares':['usr/share/applications/calamares.desktop'],
        'felunyx-calamares-config':['etc/calamares/settings.conf','etc/calamares/preinstall_copy/etc/default/grub'],
        'grub':['etc/default/grub'],
    }


def run_validator(tmp_path:Path,packages):
    profile=valid_profile(tmp_path); report=tmp_path/'report.json'; bin_dir=tmp_path/'bin'; bin_dir.mkdir()
    pacman=fake_pacman(tmp_path,packages); (bin_dir/'pacman').symlink_to(pacman)
    env=os.environ.copy(); env['PATH']=f"{bin_dir}:{env['PATH']}"
    result=subprocess.run(['tools/felunyx-validate','--profile',profile,'--report',report],env=env,check=False,capture_output=True,text=True)
    return result,json.loads(report.read_text())


def test_validator_accepts_distinct_package_ownership(tmp_path):
    result,report=run_validator(tmp_path,package_lists())
    assert result.returncode==0
    overlap=[check for check in report['checks'] if check['name'].startswith('package-overlap:')]
    assert len(overlap)==3 and all(check['status']=='pass' for check in overlap)


def test_validator_rejects_file_owned_by_grub_and_felunyx_config(tmp_path):
    packages=package_lists(); packages['felunyx-calamares-config'].append('etc/default/grub')
    result,report=run_validator(tmp_path,packages)
    assert result.returncode==1
    check=next(check for check in report['checks'] if check['name']=='package-overlap:grub:felunyx-calamares-config')
    assert check['status']=='fail' and check['detail']=='etc/default/grub'
