import subprocess
from pathlib import Path

def call(script,tmp,repo): return subprocess.run(['bash','-c',f'source tools/lib/mount_guard.sh; {script}', '_'],text=True,capture_output=True)
def test_rejects_root_and_repo(tmp_path):
    repo=Path.cwd()
    assert call(f'felunyx_assert_safe_workdir / {tmp_path} {repo}',tmp_path,repo).returncode!=0
    assert call(f'felunyx_assert_safe_workdir {repo} {tmp_path} {repo}',tmp_path,repo).returncode!=0

def test_accepts_and_removes_child(tmp_path):
    repo=Path.cwd(); work=tmp_path/'work'; work.mkdir(); (work/'x').write_text('x')
    assert call(f'felunyx_remove_workdir {work} {tmp_path} {repo}',tmp_path,repo).returncode==0
    assert not work.exists()
