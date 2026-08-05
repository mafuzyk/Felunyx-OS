from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SHA_USE = re.compile(r"uses:\s*[^\s@]+@([0-9a-f]{40})\s*$")
ROOT = Path(__file__).resolve().parents[1]
SUMMARIZER = ROOT / "tests" / "boot" / "summarize_virtual_gate.py"
SUMMARY_FIXTURE = (
    ROOT / "tests" / "fixtures" / "workflows" / "virtual-gate-summary.json"
)
REQUIRED_SCENARIOS = {
    "live_zen": "live-zen",
    "live_lts": "live-lts",
    "install": "install",
    "installed_zen": "installed-zen",
    "installed_lts": "installed-lts",
    "failure_injection": "failure-injection",
}


def workflow(name: str) -> str:
    return Path(".github/workflows", name).read_text(encoding="utf-8")


def write_scenario(root: Path, key: str, scenario: str, status: str) -> None:
    directory = root / key
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "scenario-result.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "scenario": scenario,
                "status": status,
                "started_at": "2026-08-05T12:00:00Z",
                "finished_at": "2026-08-05T12:01:00Z",
                "message": "fixture",
                "evidence": {},
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def run_summarizer(root: Path, output: Path):
    return subprocess.run(
        [
            sys.executable,
            str(SUMMARIZER),
            "--root",
            str(root),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_all_external_actions_are_full_sha_pinned():
    for path in Path(".github/workflows").glob("*.yml"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "uses:" in line:
                assert SHA_USE.search(line), f"{path}: {line}"


def test_validation_is_unprivileged_and_read_only():
    text = workflow("validate.yml")
    assert "contents: read" in text
    assert "--privileged" not in text
    assert "pull_request:" in text


def test_privileged_build_rejects_fork_prs_and_uses_no_write_permission():
    text = workflow("build-iso.yml")
    assert "head.repo.full_name == github.repository" in text
    assert "contents: read" in text
    assert "contents: write" not in text
    assert "--privileged" in text
    assert "persist-credentials: false" in text


def test_artifacts_exclude_workdirs_and_caches():
    upload = workflow("build-iso.yml").split(
        "Upload compact build evidence", 1
    )[1]
    assert "work" not in upload.lower()
    assert "cache" not in upload.lower()


def test_build_failure_preserves_full_container_log_and_exit_status():
    text = workflow("build-iso.yml")
    assert "tee artifacts/workflow-build.log" in text
    assert "build_status=${PIPESTATUS[0]}" in text
    assert 'exit "$build_status"' in text


def test_virtual_executor_pins_ovmf_variable_tooling_and_records_version():
    text = workflow("virtual-smoke.yml")
    assert "python3-virt-firmware" in text
    assert "dpkg-query -W -f='${Version}\\n' python3-virt-firmware" in text
    assert "virtual/executor-packages.txt" in text


def test_virtual_workflow_checks_out_the_artifact_source_commit():
    text = workflow("virtual-smoke.yml")
    assert "id: artifact_source" in text
    assert "build-info.json" in text
    assert "source_commit" in text
    assert "path: controller" in text
    assert "path: source" in text
    assert "ref: ${{ steps.artifact_source.outputs.source_commit }}" in text
    assert "persist-credentials: false" in text


def test_virtual_workflow_runs_every_scenario_independently():
    text = workflow("virtual-smoke.yml")
    for step_id in (*REQUIRED_SCENARIOS, "bios"):
        assert f"id: {step_id}" in text
    assert text.count("continue-on-error: true") >= 7
    assert text.count("if: always()") >= 9
    assert "--mode success" in text
    assert "--mode failure" in text
    assert "--prepare-next lts" in text
    assert "SUCCESS_DISK" in text and "FAILURE_DISK" in text
    assert "${{ env.SUCCESS_DISK }}" in text
    assert "${{ env.FAILURE_DISK }}" in text


def test_virtual_workflow_summarizes_fail_closed_and_uploads_complete_tree():
    text = workflow("virtual-smoke.yml")
    assert "controller/tests/boot/summarize_virtual_gate.py" in text
    assert "virtual/gate-summary.json" in text
    summary_step = text.split("Summarize virtual gate", 1)[1]
    assert "if: always()" in summary_step

    upload = text.split("Upload virtual evidence", 1)[1]
    assert "if: always()" in upload
    assert "path: virtual/" in upload
    assert "*.qcow2" not in upload
    assert "virtual/**/*.log" not in upload
    assert "contents: write" not in text
    assert "actions: write" not in text


def test_passing_virtual_gate_summary_matches_fixture(tmp_path: Path):
    root = tmp_path / "virtual"
    for key, scenario in REQUIRED_SCENARIOS.items():
        write_scenario(root, key, scenario, "pass")
    write_scenario(root, "bios", "bios", "not-run")
    output = root / "gate-summary.json"

    result = run_summarizer(root, output)

    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8")) == json.loads(
        SUMMARY_FIXTURE.read_text(encoding="utf-8")
    )


def test_missing_required_scenario_is_not_run_and_fails_gate(tmp_path: Path):
    root = tmp_path / "virtual"
    for key, scenario in REQUIRED_SCENARIOS.items():
        if key != "installed_lts":
            write_scenario(root, key, scenario, "pass")
    output = root / "gate-summary.json"

    result = run_summarizer(root, output)

    assert result.returncode != 0
    summary = json.loads(output.read_text(encoding="utf-8"))
    assert summary["required"]["installed_lts"] == "not-run"
    assert summary["virtual_gate"] == "fail"


def test_bios_failure_does_not_weaken_required_uefi_gate(tmp_path: Path):
    root = tmp_path / "virtual"
    for key, scenario in REQUIRED_SCENARIOS.items():
        write_scenario(root, key, scenario, "pass")
    write_scenario(root, "bios", "bios", "fail")
    output = root / "gate-summary.json"

    result = run_summarizer(root, output)

    assert result.returncode == 0, result.stderr
    summary = json.loads(output.read_text(encoding="utf-8"))
    assert summary["best_effort"]["bios"] == "fail"
    assert summary["virtual_gate"] == "pass"


def test_wrong_scenario_identity_fails_closed(tmp_path: Path):
    root = tmp_path / "virtual"
    for key, scenario in REQUIRED_SCENARIOS.items():
        write_scenario(root, key, scenario, "pass")
    write_scenario(root, "bios", "live-zen", "pass")
    output = root / "gate-summary.json"

    result = run_summarizer(root, output)

    assert result.returncode != 0
    summary = json.loads(output.read_text(encoding="utf-8"))
    assert summary["best_effort"]["bios"] == "fail"
    assert summary["virtual_gate"] == "fail"
