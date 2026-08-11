import json
import subprocess
from pathlib import Path


def test_validator_reports_missing_requirements(tmp_path):
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "packages.x86_64").write_text("linux-zen\n")
    (profile / "profiledef.sh").write_text('iso_name="bad"\n')

    report = tmp_path / "report.json"
    result = subprocess.run(
        ["tools/felunyx-validate", "--profile", profile, "--report", report]
    )

    data = json.loads(report.read_text())
    assert result.returncode == 1
    assert data["status"] == "fail"
    assert report.stat().st_mode & 0o777 == 0o644
