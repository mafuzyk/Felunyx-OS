from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "evidence"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def run_live_payload(payload: dict, tmp_path: Path, kernel: str = "zen"):
    serial = tmp_path / "serial.log"
    serial.write_text(
        "FELUNYX_EVIDENCE=" + json.dumps(payload, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "live-evidence.json"
    result = subprocess.run(
        [
            sys.executable,
            "tests/boot/expect_serial.py",
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


def test_installer_uses_accessibility_not_coordinates():
    text = Path("packages/felunyx-iso-hooks/drive-installation.py").read_text()
    assert "pyatspi" in text
    for forbidden in ("xdotool", "pyautogui", "moveTo(", "click(" + "x="):
        assert forbidden not in text


def test_evidence_is_opt_in_and_serialized():
    text = Path("packages/felunyx-identity/felunyx-evidence").read_text()
    assert "qemu_fw_cfg" in text and "FELUNYX_EVIDENCE=" in text
    unit = Path("packages/felunyx-identity/felunyx-evidence.service").read_text()
    assert "Type=oneshot" in unit


def test_guest_live_collector_declares_schema2_session_state():
    path = Path("packages/felunyx-identity/felunyx-evidence")
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))

    has_schema2 = any(
        isinstance(node, ast.Dict)
        and any(
            isinstance(key, ast.Constant)
            and key.value == "schema"
            and isinstance(value, ast.Constant)
            and value.value == 2
            for key, value in zip(node.keys, node.values)
        )
        for node in ast.walk(tree)
    )
    assert has_schema2
    for required in (
        "loginctl",
        "/sys/firmware/efi",
        "/usr/lib/felunyx/build-info.json",
        "/usr/share/wayland-sessions/plasma.desktop",
        "sshd.socket",
    ):
        assert required in text

    unit = Path(
        "packages/felunyx-identity/felunyx-evidence.service"
    ).read_text(encoding="utf-8")
    assert "After=graphical.target display-manager.service" in unit
    assert "Wants=display-manager.service" in unit
    assert "WantedBy=graphical.target" in unit

    pkgbuild = Path("packages/felunyx-identity/PKGBUILD").read_text(
        encoding="utf-8"
    )
    assert "systemd/system/graphical.target.wants" in pkgbuild
    assert "systemd/system/multi-user.target.wants" not in pkgbuild


def test_grub_has_serial_and_stable_zen_default():
    text = Path("packages/felunyx-calamares-config/grub-default").read_text()
    assert "GRUB_TOP_LEVEL=/boot/vmlinuz-linux-zen" in text
    assert "console=ttyS0,115200n8" in text


def test_valid_live_evidence_is_persisted(tmp_path: Path):
    payload = load_fixture("live-zen-valid.json")
    result, output = run_live_payload(payload, tmp_path)

    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8")) == payload


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("uefi", "required UEFI boot was not observed"),
        ("graphical_target", "graphical target is inactive"),
        ("sddm", "SDDM is inactive"),
        ("networkmanager", "NetworkManager is inactive"),
        ("plasma_wayland_available", "Plasma Wayland definition is absent"),
    ],
)
def test_live_evidence_rejects_false_required_state(
    tmp_path: Path, field: str, message: str
):
    payload = load_fixture("live-zen-valid.json")
    payload[field] = False

    result, output = run_live_payload(payload, tmp_path)

    assert result.returncode != 0
    assert message in result.stderr
    assert not output.exists()


@pytest.mark.parametrize(
    "field",
    [
        "uefi",
        "graphical_target",
        "sddm",
        "networkmanager",
        "plasma_wayland_available",
        "sessions",
    ],
)
def test_live_evidence_rejects_missing_required_key(tmp_path: Path, field: str):
    payload = load_fixture("live-zen-valid.json")
    payload.pop(field)

    result, output = run_live_payload(payload, tmp_path)

    assert result.returncode != 0
    assert f"missing required key: {field}" in result.stderr
    assert not output.exists()


def test_live_evidence_requires_active_plasma_wayland(tmp_path: Path):
    payload = load_fixture("live-missing-plasma.json")

    result, output = run_live_payload(payload, tmp_path)

    assert result.returncode != 0
    assert "active Plasma Wayland session is absent" in result.stderr
    assert not output.exists()
