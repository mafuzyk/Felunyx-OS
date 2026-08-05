from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WRITER = ROOT / "tests" / "boot" / "write_scenario_result.py"
INSTALL_ASSERT = ROOT / "tests" / "boot" / "assert_installer_outcome.py"
EXPECT_SERIAL = ROOT / "tests" / "boot" / "expect_serial.py"
LIVE_FIXTURE = ROOT / "tests" / "fixtures" / "evidence" / "live-zen-valid.json"


def run_writer(tmp_path: Path, status: str = "pass"):
    output = tmp_path / "scenario-result.json"
    result = subprocess.run(
        [
            sys.executable,
            str(WRITER),
            "--output",
            str(output),
            "--scenario",
            "live-zen",
            "--status",
            status,
            "--started-at",
            "2026-08-05T12:00:00Z",
            "--finished-at",
            "2026-08-05T12:01:00Z",
            "--message",
            "validated",
            "--evidence",
            "serial=serial.log",
            "--evidence",
            "live=live-evidence.json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result, output


def log_record(name: str, content: bytes) -> str:
    return "FELUNYX_INSTALL_LOG=" + json.dumps(
        {
            "schema": 1,
            "name": name,
            "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "content_base64": base64.b64encode(content).decode("ascii"),
        },
        sort_keys=True,
    )


def run_installer_assertion(
    tmp_path: Path,
    mode: str,
    events: list[dict],
    logs: dict[str, bytes],
):
    serial = tmp_path / "serial.log"
    serial.write_text(
        "".join(
            "FELUNYX_INSTALL=" + json.dumps(event, sort_keys=True) + "\n"
            for event in events
        ),
        encoding="utf-8",
    )
    stream = tmp_path / "guest-evidence.stream"
    stream.write_text(
        "\n".join(log_record(name, content) for name, content in logs.items())
        + ("\n" if logs else ""),
        encoding="utf-8",
    )
    output = tmp_path / "installer-outcome.json"
    extracted = tmp_path / "guest-logs"
    result = subprocess.run(
        [
            sys.executable,
            str(INSTALL_ASSERT),
            "--serial",
            str(serial),
            "--evidence-stream",
            str(stream),
            "--mode",
            mode,
            "--output",
            str(output),
            "--logs-dir",
            str(extracted),
            "--timeout",
            "1",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result, output, extracted


def test_scenario_result_writer_is_atomic_and_structured(tmp_path: Path):
    result, output = run_writer(tmp_path)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "schema": 1,
        "scenario": "live-zen",
        "status": "pass",
        "started_at": "2026-08-05T12:00:00Z",
        "finished_at": "2026-08-05T12:01:00Z",
        "message": "validated",
        "evidence": {
            "live": "live-evidence.json",
            "serial": "serial.log",
        },
    }
    assert not list(tmp_path.glob(".scenario-result.json.*"))


def test_scenario_result_writer_rejects_unknown_status(tmp_path: Path):
    result, output = run_writer(tmp_path, "greenish")
    assert result.returncode == 64
    assert "unsupported scenario status" in result.stderr
    assert not output.exists()


def test_successful_installer_outcome_is_exact_and_extracts_logs(tmp_path: Path):
    events = [
        {"event": "start", "mode": "success"},
        {"event": "stage", "stage": "installation-confirmed"},
        {"event": "success", "mode": "success"},
    ]
    logs = {"installer-harness.log": b"success evidence\n"}
    result, output, extracted = run_installer_assertion(
        tmp_path, "success", events, logs
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads(output.read_text(encoding="utf-8"))
    assert summary["mode"] == "success"
    assert summary["outcome"] == "success"
    assert summary["logs"] == ["installer-harness.log"]
    assert (extracted / "installer-harness.log").read_bytes() == logs[
        "installer-harness.log"
    ]


def test_expected_failure_requires_class_and_actionable_logs(tmp_path: Path):
    events = [
        {"event": "start", "mode": "failure"},
        {
            "event": "failure",
            "stage": "felunyx-fail",
            "error_class": "FelunyxInjectedFailure",
        },
    ]
    logs = {
        "installer-harness.log": b"harness failure\n",
        "calamares-debug.log": b"FelunyxInjectedFailure\n",
    }
    result, output, extracted = run_installer_assertion(
        tmp_path, "failure", events, logs
    )
    assert result.returncode == 0, result.stderr
    summary = json.loads(output.read_text(encoding="utf-8"))
    assert summary["outcome"] == "expected-failure"
    assert summary["error_class"] == "FelunyxInjectedFailure"
    assert sorted(summary["logs"]) == sorted(logs)
    for name, content in logs.items():
        assert (extracted / name).read_bytes() == content


@pytest.mark.parametrize(
    ("events", "message"),
    [
        (
            [
                {"event": "start", "mode": "failure"},
                {"event": "success", "mode": "failure"},
            ],
            "unexpected installer success in failure mode",
        ),
        (
            [
                {"event": "start", "mode": "failure"},
                {"event": "blocked", "error": "random crash"},
            ],
            "installer was blocked instead of reaching expected failure",
        ),
        (
            [
                {"event": "start", "mode": "failure"},
                {
                    "event": "failure",
                    "stage": "other",
                    "error_class": "OtherFailure",
                },
            ],
            "unexpected installer failure classification",
        ),
    ],
)
def test_failure_mode_rejects_false_success_or_unrelated_failure(
    tmp_path: Path, events: list[dict], message: str
):
    logs = {
        "installer-harness.log": b"harness\n",
        "calamares-debug.log": b"debug\n",
    }
    result, output, _ = run_installer_assertion(
        tmp_path, "failure", events, logs
    )
    assert result.returncode != 0
    assert message in result.stderr
    assert not output.exists()


def test_failure_mode_rejects_missing_actionable_logs(tmp_path: Path):
    events = [
        {"event": "start", "mode": "failure"},
        {
            "event": "failure",
            "stage": "felunyx-fail",
            "error_class": "FelunyxInjectedFailure",
        },
    ]
    result, output, _ = run_installer_assertion(
        tmp_path,
        "failure",
        events,
        {"installer-harness.log": b"only one log\n"},
    )
    assert result.returncode != 0
    assert "required failure log is absent: calamares-debug.log" in result.stderr
    assert not output.exists()


def test_installer_log_transport_rejects_unsafe_name_and_bad_hash(tmp_path: Path):
    events = [
        {"event": "start", "mode": "success"},
        {"event": "success", "mode": "success"},
    ]
    serial = tmp_path / "serial.log"
    serial.write_text(
        "".join(
            "FELUNYX_INSTALL=" + json.dumps(event) + "\n"
            for event in events
        ),
        encoding="utf-8",
    )
    stream = tmp_path / "stream"
    stream.write_text(
        "FELUNYX_INSTALL_LOG="
        + json.dumps(
            {
                "schema": 1,
                "name": "../escape.log",
                "size": 3,
                "sha256": "0" * 64,
                "content_base64": base64.b64encode(b"bad").decode(),
            }
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "out.json"
    result = subprocess.run(
        [
            sys.executable,
            str(INSTALL_ASSERT),
            "--serial",
            str(serial),
            "--evidence-stream",
            str(stream),
            "--mode",
            "success",
            "--output",
            str(output),
            "--logs-dir",
            str(tmp_path / "logs"),
            "--timeout",
            "1",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "unsafe installer log name" in result.stderr
    assert not output.exists()


def test_bios_live_evidence_allows_bios_but_stays_strict(tmp_path: Path):
    payload = json.loads(LIVE_FIXTURE.read_text(encoding="utf-8"))
    payload["uefi"] = False
    serial = tmp_path / "serial.log"
    serial.write_text(
        "FELUNYX_EVIDENCE=" + json.dumps(payload) + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "bios-evidence.json"
    result = subprocess.run(
        [
            sys.executable,
            str(EXPECT_SERIAL),
            "--log",
            str(serial),
            "--kernel",
            "zen",
            "--firmware",
            "bios",
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
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8"))["uefi"] is False


def test_vm_harness_defines_independent_fail_closed_scenarios():
    text = Path("tools/felunyx-run-vm").read_text(encoding="utf-8")
    for required in (
        "boot-live",
        "install",
        "boot-installed",
        "boot-bios",
        "--mode",
        "success|failure",
        "scenario-result.json",
        "write_scenario_result.py",
        "qemu.stderr.log",
        "qmp-diagnostics.json",
        "guest-evidence.stream",
        "org.felunyx.evidence",
        "assert_installer_outcome.py",
        "preserve_diagnostics",
        "trap",
    ):
        assert required in text

    assert "qemu-system-x86_64 \"${args[@]}\" 2>\"$qemu_stderr\" &" in text
    assert "OVMF_VARS.fd" in text and "qmp.sock" in text
    assert "qmp_sendkey.py" not in text
    assert "failure installation disk already exists" in text

    for line in text.splitlines():
        if any(
            validator in line
            for validator in (
                "expect_serial.py",
                "assert_installed_system.py",
                "assert_grub_oneshot.py",
                "assert_installer_outcome.py",
            )
        ):
            assert "|| true" not in line


def test_installer_driver_transports_retained_logs_over_dedicated_port():
    text = Path(
        "packages/felunyx-iso-hooks/drive-installation.py"
    ).read_text(encoding="utf-8")
    for required in (
        "/dev/virtio-ports/org.felunyx.evidence",
        "FELUNYX_INSTALL_LOG=",
        "content_base64",
        "sha256",
        "preserve_logs()",
    ):
        assert required in text
