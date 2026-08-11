import grp
import os
import pwd
import shutil
import subprocess
import tempfile
from pathlib import Path


def _prepare(work: Path, private_dir: Path, user: str, group: str) -> None:
    script = (
        "source tools/lib/build_user.sh; "
        f"felunyx_prepare_builder_private_dir '{work}' '{private_dir}' '{user}' '{group}'"
    )
    subprocess.run(["bash", "-c", script], check=True)


def test_private_builder_directory_keeps_privacy_and_parent_traversal():
    user = pwd.getpwuid(os.getuid()).pw_name
    group = grp.getgrgid(os.getgid()).gr_name
    work = Path(tempfile.mkdtemp(prefix="felunyx-permissions-", dir="/tmp"))
    private_dir = work / "gnupg"
    try:
        work.chmod(0o700)
        _prepare(work, private_dir, user, group)
        assert (work.stat().st_mode & 0o777) == 0o711
        assert (private_dir.stat().st_mode & 0o777) == 0o700
        assert os.access(private_dir, os.X_OK)
    finally:
        shutil.rmtree(work)


def test_unprivileged_builder_can_reach_private_directory_when_running_as_root():
    if os.geteuid() != 0:
        return
    user = pwd.getpwnam("nobody")
    work = Path(tempfile.mkdtemp(prefix="felunyx-runuser-", dir="/tmp"))
    private_dir = work / "gnupg"
    try:
        work.chmod(0o700)
        _prepare(work, private_dir, "nobody", str(user.pw_gid))
        result = subprocess.run(
            ["runuser", "-u", "nobody", "--", "test", "-x", str(private_dir)],
            check=False,
        )
        assert result.returncode == 0
    finally:
        shutil.rmtree(work)
