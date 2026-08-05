import re
from pathlib import Path

SHA_USE=re.compile(r'uses:\s*[^\s@]+@([0-9a-f]{40})\s*$')
def workflow(name): return Path('.github/workflows',name).read_text()

def test_all_external_actions_are_full_sha_pinned():
    for path in Path('.github/workflows').glob('*.yml'):
        for line in path.read_text().splitlines():
            if 'uses:' in line: assert SHA_USE.search(line),f'{path}: {line}'

def test_validation_is_unprivileged_and_read_only():
    text=workflow('validate.yml'); assert 'contents: read' in text; assert '--privileged' not in text; assert 'pull_request:' in text

def test_privileged_build_rejects_fork_prs_and_uses_no_write_permission():
    text=workflow('build-iso.yml'); assert "head.repo.full_name == github.repository" in text; assert 'contents: read' in text; assert 'contents: write' not in text; assert '--privileged' in text; assert 'persist-credentials: false' in text

def test_artifacts_exclude_workdirs_and_caches():
    upload=workflow('build-iso.yml').split('Upload compact build evidence',1)[1]; assert 'work' not in upload.lower(); assert 'cache' not in upload.lower()

def test_build_failure_preserves_full_container_log_and_exit_status():
    text=workflow('build-iso.yml')
    assert 'tee artifacts/workflow-build.log' in text
    assert 'build_status=${PIPESTATUS[0]}' in text
    assert 'exit "$build_status"' in text


def test_virtual_executor_pins_ovmf_variable_tooling_and_records_version():
    text = workflow('virtual-smoke.yml')
    assert 'python3-virt-firmware' in text
    assert "dpkg-query -W -f='${Version}\\n' python3-virt-firmware" in text
    assert 'virtual/executor-packages.txt' in text
