from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "evidence"
ASSERT_INSTALLED = ROOT / "tests" / "boot" / "assert_installed_system.py"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def run_payload(payload: dict, tmp_path: Path, kernel: str = "zen"):
    serial = tmp_path / "serial.log"
    serial.write_text(
        "FELUNYX_INSTALLED=" + json.dumps(payload, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "installed-evidence.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ASSERT_INSTALLED),
            "--log",
            str(serial),
            "--kernel",
            kernel,
            "--output",
            str(output),
            "--timeout",
            "1",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result, output


def test_valid_installed_evidence_is_persisted(tmp_path: Path):
    payload = fixture("installed-zen-valid.json")
    result, output = run_payload(payload, tmp_path)

    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8")) == payload


def test_installed_evidence_rejects_wrong_root_subvolume(tmp_path: Path):
    result, output = run_payload(
        fixture("installed-wrong-btrfs.json"), tmp_path
    )

    assert result.returncode != 0
    assert "wrong Btrfs subvolume for /" in result.stderr
    assert not output.exists()


@pytest.mark.parametrize(
    ("section", "field", "value", "message"),
    [
        ("packages", "grub", False, "required package absent: grub"),
        ("packages", "linux-zen", False, "required package absent: linux-zen"),
        ("packages", "linux-lts", False, "required package absent: linux-lts"),
        (
            "packages",
            "felunyx-iso-hooks",
            True,
            "live-only package remains installed",
        ),
        ("files", "live_marker", True, "live marker remains installed"),
        ("files", "live_sudo", True, "live sudo policy remains installed"),
        (
            "files",
            "live_autologin",
            True,
            "live autologin policy remains installed",
        ),
        (
            "services",
            "sshd_service_active",
            True,
            "SSH service is active",
        ),
        (
            "services",
            "sshd_socket_active",
            True,
            "SSH socket is active",
        ),
    ],
)
def test_installed_evidence_rejects_policy_or_package_residue(
    tmp_path: Path,
    section: str,
    field: str,
    value: bool,
    message: str,
):
    payload = fixture("installed-zen-valid.json")
    payload[section][field] = value

    result, output = run_payload(payload, tmp_path)

    assert result.returncode != 0
    assert message in result.stderr
    assert not output.exists()


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("grub_cfg", "GRUB configuration is absent"),
        ("linux_zen_kernel", "Linux Zen kernel image is absent"),
        ("linux_lts_kernel", "Linux LTS kernel image is absent"),
    ],
)
def test_installed_evidence_rejects_missing_boot_payload(
    tmp_path: Path, field: str, message: str
):
    payload = fixture("installed-zen-valid.json")
    payload["files"][field]["exists"] = False
    payload["files"][field]["size"] = 0

    result, output = run_payload(payload, tmp_path)

    assert result.returncode != 0
    assert message in result.stderr
    assert not output.exists()


def test_installed_evidence_requires_compression_and_efi_mask(tmp_path: Path):
    payload = fixture("installed-zen-valid.json")
    payload["mounts"]["/home"]["options"].remove("compress=zstd:1")
    result, output = run_payload(payload, tmp_path)
    assert result.returncode != 0
    assert "missing compress=zstd:1 on /home" in result.stderr
    assert not output.exists()

    payload = fixture("installed-zen-valid.json")
    payload["mounts"]["/boot/efi"]["options"].remove("umask=0077")
    result, output = run_payload(payload, tmp_path)
    assert result.returncode != 0
    assert "EFI mount mask is not 0077" in result.stderr
    assert not output.exists()


def test_installed_evidence_rejects_duplicate_success_payload(tmp_path: Path):
    payload = fixture("installed-zen-valid.json")
    serial = tmp_path / "serial.log"
    line = "FELUNYX_INSTALLED=" + json.dumps(payload, sort_keys=True) + "\n"
    serial.write_text(line + line, encoding="utf-8")
    output = tmp_path / "installed-evidence.json"

    result = subprocess.run(
        [
            sys.executable,
            str(ASSERT_INSTALLED),
            "--log",
            str(serial),
            "--kernel",
            "zen",
            "--output",
            str(output),
            "--timeout",
            "1",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "duplicate installed evidence" in result.stderr
    assert not output.exists()


def test_guest_installed_collector_is_packaged_and_read_only():
    collector = Path(
        "packages/felunyx-identity/felunyx-installed-evidence"
    )
    assert collector.is_file()
    text = collector.read_text(encoding="utf-8")
    for required in (
        "FELUNYX_INSTALLED=",
        "pacman",
        "findmnt",
        "btrfs",
        "/etc/fstab",
        "/boot/grub/grub.cfg",
        "/boot/vmlinuz-linux-zen",
        "/boot/vmlinuz-linux-lts",
        "sshd.socket",
    ):
        assert required in text
    for forbidden in (
        "pacman -S",
        "grub-mkconfig",
        "btrfs subvolume create",
        "systemctl enable",
        "mount -o",
    ):
        assert forbidden not in text

    service = Path(
        "packages/felunyx-identity/felunyx-evidence.service"
    ).read_text(encoding="utf-8")
    live = "ExecStart=/usr/lib/felunyx/felunyx-evidence"
    installed = "ExecStart=/usr/lib/felunyx/felunyx-installed-evidence"
    assert live in service and installed in service
    assert service.index(live) < service.index(installed)

    pkgbuild = Path("packages/felunyx-identity/PKGBUILD").read_text(
        encoding="utf-8"
    )
    assert "felunyx-installed-evidence" in pkgbuild
    assert (
        'install -Dm0755 "$srcdir/felunyx-installed-evidence"' in pkgbuild
    )


def test_installed_boot_uses_strict_assertion_and_semantic_lts_handoff():
    text = Path("tools/felunyx-run-vm").read_text(encoding="utf-8")
    assert "assert_installed_system.py" in text
    assert "installed-evidence.json" in text
    assert "--prepare-next" in text
    assert "assert_grub_oneshot.py" in text
    assert "installed LTS selection is blocked" not in text
    assert "boot-installed is blocked until strict installed evidence" not in text
