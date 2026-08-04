from pathlib import Path

def test_os_release_identity():
    text=Path('packages/felunyx-identity/os-release').read_text()
    assert 'ID=felunyx' in text
    assert 'ID_LIKE=arch' in text
    assert 'PRETTY_NAME="Felunyx OS Phase 2"' in text

def test_live_policy_is_explicit_and_limited():
    sudo=Path('packages/felunyx-iso-hooks/10-felunyx-live')
    assert 'live ALL=' in sudo.read_text()
    pkg=Path('packages/felunyx-iso-hooks/PKGBUILD').read_text()
    assert 'install -Dm0440' in pkg
    assert 'sshd.service' in pkg and '/dev/null' in pkg
    assert 'felunyx-live-setup.service' in Path('packages/felunyx-iso-hooks/felunyx-live.preset').read_text()

def test_build_info_requires_explicit_provenance():
    pkg=Path('packages/felunyx-identity/PKGBUILD').read_text()
    for name in ('FELUNYX_SOURCE_COMMIT','FELUNYX_ARCHIVE_DATE','SOURCE_DATE_EPOCH'):
        assert f'${{{name}:?' in pkg
