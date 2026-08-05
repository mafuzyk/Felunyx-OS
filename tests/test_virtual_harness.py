from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "evidence"
LOADER_HELPER = ROOT / "tests" / "boot" / "set_loader_oneshot.py"
SYSTEMD_BOOT_GUID = "4a67b082-0a4c-41cf-b6c7-440b29bb8c4f"


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


def install_fake_virt_fw_tools(tmp_path: Path) -> tuple[Path, Path]:
    bindir = tmp_path / "bin"
    bindir.mkdir()
    capture = tmp_path / "set-json-capture.json"

    virt_fw_vars = bindir / "virt-fw-vars"
    virt_fw_vars.write_text(
        """#!/usr/bin/env python3
import json
import os
import shutil
import sys
from pathlib import Path

args = sys.argv[1:]
def value(flag):
    return args[args.index(flag) + 1]

if '--set-json' in args:
    payload = Path(value('--set-json'))
    Path(os.environ['FELUNYX_FAKE_CAPTURE']).write_text(
        payload.read_text(encoding='utf-8'), encoding='utf-8'
    )
    shutil.copyfile(value('--input'), value('--output'))
    raise SystemExit(0)

if '--output-json' in args:
    entry = os.environ['FELUNYX_FAKE_READBACK_ENTRY']
    data = (entry + '\\0').encode('utf-16-le').hex()
    result = {
        'variables': [{
            'name': 'LoaderEntryOneShot',
            'guid': '4a67b082-0a4c-41cf-b6c7-440b29bb8c4f',
            'attr': 7,
            'data': data,
        }]
    }
    Path(value('--output-json')).write_text(
        json.dumps(result), encoding='utf-8'
    )
    raise SystemExit(0)

raise SystemExit(2)
""",
        encoding="utf-8",
    )
    virt_fw_vars.chmod(0o755)

    dpkg_query = bindir / "dpkg-query"
    dpkg_query.write_text(
        "#!/bin/sh\nprintf '%s\\n' '24.1.1-2'\n",
        encoding="utf-8",
    )
    dpkg_query.chmod(0o755)
    return bindir, capture


def run_loader_helper(
    tmp_path: Path,
    entry: str,
    *,
    readback_entry: str | None = None,
    with_tools: bool = True,
):
    vars_path = tmp_path / "OVMF_VARS.fd"
    vars_path.write_bytes(b"test-varstore")
    report = tmp_path / "loader-entry-oneshot.json"
    env = os.environ.copy()

    if with_tools:
        bindir, capture = install_fake_virt_fw_tools(tmp_path)
        env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
        env["FELUNYX_FAKE_CAPTURE"] = str(capture)
        env["FELUNYX_FAKE_READBACK_ENTRY"] = readback_entry or entry
    else:
        capture = tmp_path / "unused-capture.json"
        env["PATH"] = ""

    result = subprocess.run(
        [
            sys.executable,
            str(LOADER_HELPER),
            "--vars",
            str(vars_path),
            "--entry",
            entry,
            "--report",
            str(report),
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    return result, report, capture


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


def test_evidence_service_avoids_graphical_target_ordering_cycle():
    unit = Path(
        "packages/felunyx-identity/felunyx-evidence.service"
    ).read_text(encoding="utf-8")
    assert "After=display-manager.service" in unit
    assert "After=graphical.target" not in unit
    assert "Wants=display-manager.service" in unit
    assert "WantedBy=graphical.target" in unit

    pkgbuild = Path("packages/felunyx-identity/PKGBUILD").read_text(
        encoding="utf-8"
    )
    assert "systemd/system/graphical.target.wants" in pkgbuild
    assert "systemd/system/multi-user.target.wants" not in pkgbuild


def test_evidence_service_timeout_exceeds_session_wait_budget():
    unit = Path(
        "packages/felunyx-identity/felunyx-evidence.service"
    ).read_text(encoding="utf-8")
    assert "TimeoutStartSec=150s" in unit


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


def test_live_kernel_selection_removes_timed_qmp_navigation():
    text = Path("tools/felunyx-run-vm").read_text(encoding="utf-8")
    assert "qmp_sendkey.py" not in text
    assert "sleep 2" not in text
    assert " down ret" not in text
    assert "set_loader_oneshot.py" in text
    assert "loader-entry-oneshot.json" in text


def test_loader_oneshot_rejects_unknown_entry(tmp_path: Path):
    result, report, _ = run_loader_helper(
        tmp_path, "felunyx-linux-debug.conf"
    )

    assert result.returncode == 64
    assert "unsupported loader entry" in result.stderr
    assert not report.exists()


def test_loader_oneshot_rejects_missing_tool(tmp_path: Path):
    result, report, _ = run_loader_helper(
        tmp_path, "felunyx-linux-lts.conf", with_tools=False
    )

    assert result.returncode != 0
    assert "virt-fw-vars is required" in result.stderr
    assert not report.exists()


def test_loader_oneshot_writes_hex_payload_and_verified_report(tmp_path: Path):
    entry = "felunyx-linux-lts.conf"
    result, report, capture = run_loader_helper(tmp_path, entry)

    assert result.returncode == 0, result.stderr
    payload = json.loads(capture.read_text(encoding="utf-8"))
    variable = payload["variables"][0]
    assert variable == {
        "name": "LoaderEntryOneShot",
        "guid": SYSTEMD_BOOT_GUID,
        "attr": 7,
        "data": (entry + "\0").encode("utf-16-le").hex(),
    }

    recorded = json.loads(report.read_text(encoding="utf-8"))
    assert recorded == {
        "schema": 1,
        "tool_package": "python3-virt-firmware",
        "tool_version": "24.1.1-2",
        "guid": SYSTEMD_BOOT_GUID,
        "variable": "LoaderEntryOneShot",
        "entry": entry,
        "verified": True,
    }


def test_loader_oneshot_rejects_readback_mismatch(tmp_path: Path):
    result, report, _ = run_loader_helper(
        tmp_path,
        "felunyx-linux-lts.conf",
        readback_entry="felunyx-linux-zen.conf",
    )

    assert result.returncode != 0
    assert "LoaderEntryOneShot readback mismatch" in result.stderr
    assert not report.exists()
