from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUEST_HELPER = ROOT / "packages" / "felunyx-identity" / "felunyx-prepare-grub-oneshot"
HOST_ASSERT = ROOT / "tests" / "boot" / "assert_grub_oneshot.py"
FIXTURE = ROOT / "tests" / "fixtures" / "grub" / "grub.cfg"
EXPECTED_SELECTOR = (
    "gnulinux-advanced-ROOTUUID>"
    "gnulinux-linux-lts-advanced-ROOTUUID"
)


def load_guest_helper():
    assert GUEST_HELPER.is_file()
    loader = importlib.machinery.SourceFileLoader(
        "felunyx_prepare_grub_oneshot", str(GUEST_HELPER)
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def run_host_payload(payload: dict, tmp_path: Path):
    serial = tmp_path / "serial.log"
    serial.write_text(
        "FELUNYX_GRUB_NEXT=" + json.dumps(payload, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "grub-next.json"
    result = subprocess.run(
        [
            sys.executable,
            str(HOST_ASSERT),
            "--log",
            str(serial),
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


def valid_payload() -> dict:
    return {
        "schema": 1,
        "requested": "linux-lts",
        "selector": EXPECTED_SELECTOR,
        "verified": True,
    }


def test_parser_selects_lts_only_by_grub_ids():
    module = load_guest_helper()
    selector = module.parse_lts_selector(FIXTURE.read_text(encoding="utf-8"))
    assert selector == EXPECTED_SELECTOR
    assert not selector[0].isdigit()
    assert "Felunyx OS" not in selector


def test_parser_rejects_lts_entry_without_id():
    module = load_guest_helper()
    text = FIXTURE.read_text(encoding="utf-8").replace(
        "$menuentry_id_option 'gnulinux-linux-lts-advanced-ROOTUUID'",
        "",
    )
    with pytest.raises(ValueError, match="LTS menuentry ID"):
        module.parse_lts_selector(text)


def test_parser_rejects_multiple_lts_entries():
    module = load_guest_helper()
    text = FIXTURE.read_text(encoding="utf-8") + """
submenu 'Other' --id other-submenu {
  menuentry 'Other LTS' --id other-lts {
    linux /boot/vmlinuz-linux-lts root=UUID=OTHER rw
  }
}
"""
    with pytest.raises(ValueError, match="exactly one Linux LTS entry"):
        module.parse_lts_selector(text)


def test_parser_rejects_entry_that_does_not_load_lts_kernel():
    module = load_guest_helper()
    text = FIXTURE.read_text(encoding="utf-8").replace(
        "/boot/vmlinuz-linux-lts", "/boot/vmlinuz-linux-zen"
    )
    with pytest.raises(ValueError, match="exactly one Linux LTS entry"):
        module.parse_lts_selector(text)


def test_valid_grub_oneshot_evidence_is_persisted(tmp_path: Path):
    payload = valid_payload()
    result, output = run_host_payload(payload, tmp_path)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8")) == payload


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("schema", 2, "GRUB one-shot schema must be 1"),
        ("requested", "linux-zen", "unexpected GRUB one-shot request"),
        ("verified", False, "GRUB one-shot was not verified"),
        ("selector", "1>0", "GRUB selector must use stable IDs"),
        ("selector", "gnulinux-linux-lts", "GRUB selector must include submenu and entry IDs"),
    ],
)
def test_grub_oneshot_rejects_unverified_or_unstable_selector(
    tmp_path: Path, field: str, value: object, message: str
):
    payload = valid_payload()
    payload[field] = value
    result, output = run_host_payload(payload, tmp_path)
    assert result.returncode != 0
    assert message in result.stderr
    assert not output.exists()


def test_grub_oneshot_rejects_duplicate_marker(tmp_path: Path):
    payload = valid_payload()
    line = "FELUNYX_GRUB_NEXT=" + json.dumps(payload, sort_keys=True) + "\n"
    serial = tmp_path / "serial.log"
    serial.write_text(line + line, encoding="utf-8")
    output = tmp_path / "grub-next.json"
    result = subprocess.run(
        [
            sys.executable,
            str(HOST_ASSERT),
            "--log",
            str(serial),
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
    assert "duplicate GRUB one-shot evidence" in result.stderr
    assert not output.exists()


def test_guest_helper_is_opt_in_one_shot_and_packaged():
    assert GUEST_HELPER.is_file()
    text = GUEST_HELPER.read_text(encoding="utf-8")
    for required in (
        "opt/felunyx/grub-next/raw",
        "/boot/grub/grub.cfg",
        "grub-reboot",
        "grub-editenv",
        "next_entry=",
        "FELUNYX_GRUB_NEXT=",
        "systemctl",
        "poweroff",
    ):
        assert required in text
    for forbidden in (
        "grub-set-default",
        "GRUB_DEFAULT=",
        "saved_entry=",
    ):
        assert forbidden not in text

    service = Path(
        "packages/felunyx-identity/felunyx-evidence.service"
    ).read_text(encoding="utf-8")
    installed = "ExecStart=/usr/lib/felunyx/felunyx-installed-evidence"
    prepare = "ExecStart=/usr/lib/felunyx/felunyx-prepare-grub-oneshot"
    assert installed in service and prepare in service
    assert service.index(installed) < service.index(prepare)

    pkgbuild = Path("packages/felunyx-identity/PKGBUILD").read_text(
        encoding="utf-8"
    )
    assert "felunyx-prepare-grub-oneshot" in pkgbuild
    assert (
        'install -Dm0755 "$srcdir/felunyx-prepare-grub-oneshot"'
        in pkgbuild
    )


def test_installed_harness_prepares_lts_and_allows_followup_boot():
    text = Path("tools/felunyx-run-vm").read_text(encoding="utf-8")
    assert "--prepare-next" in text
    assert "opt/felunyx/grub-next,string=linux-lts" in text
    assert "assert_grub_oneshot.py" in text
    assert "grub-next.json" in text
    assert "installed LTS selection is blocked" not in text
    assert "qmp_sendkey.py" not in text
