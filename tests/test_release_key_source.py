from pathlib import Path


def test_release_key_source_requires_complete_identity_and_exact_fingerprint():
    script = Path('tools/felunyx-build').read_text()
    assert 'hkp://keyserver.ubuntu.com:80' in script
    assert 'keys.openpgp.org' not in script
    assert 'uid_count=' in script
    assert 'Calamares signing key has no usable user identity' in script
    assert 'actual_fingerprint == "$key_fingerprint"' in script
