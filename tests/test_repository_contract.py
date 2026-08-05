from pathlib import Path


def test_core_scripts_are_strict():
    for path in Path("tools").glob("felunyx-*"):
        text = path.read_text(encoding="utf-8")
        if text.startswith("#!/usr/bin/env bash"):
            assert "set -Eeuo pipefail" in text, path


def test_expected_roots_exist():
    for root in ("build", "tools", "tests", "iso"):
        assert Path(root).exists()


def test_phase2_status_is_current_and_honest():
    text = Path("docs/status/phase-2-reproducible-iso.md").read_text(
        encoding="utf-8"
    )

    for required in (
        "PR #3",
        "agent/phase-2-implementation",
        "1f89d17b10c8e0b4965a7f8ebc5e4d509e5f637a",
        "draft and unmerged",
        "PR #5",
        "fix/phase-2-virtual-gate-hardening",
        "31007003860",
        "132 tests passed",
        "30951476281",
        "felunyx-phase2-30951476281",
        "sha256:cf130079fdf93b1fd6a7deb2581135882fe9fdb2fcbf1bb2c77881087733cd10",
        "internal development artifact",
        "not a release",
        "predates the guest-side hardening",
        "Remote gate | pending",
        "Virtual gate | pending",
        "Hardware gate | not tested",
        "matching rebuilt ISO",
        "comparison evidence",
        "PR #6",
        "preparatory design only",
        "Phase 3 implementation remains blocked",
    ):
        assert required in text

    for vocabulary in (
        "implemented",
        "validated remotely",
        "validated in VM",
        "validated in hardware",
        "pending",
        "not tested",
    ):
        assert f"`{vocabulary}`" in text

    assert "Implementation | Ready to start" not in text
    assert "Remote gate | validated remotely" not in text
    assert "Virtual gate | validated in VM" not in text
    assert "Hardware gate | validated in hardware" not in text
