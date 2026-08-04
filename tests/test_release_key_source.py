from pathlib import Path


def test_release_key_source_uses_https_and_exact_cryptographic_identity():
    script = Path('tools/felunyx-build').read_text()
    assert 'https://github.com/adriaandegroot.gpg' in script
    assert '--keyserver' not in script
    assert '--recv-keys' not in script
    assert 'import-options import-minimal' in script
    assert 'uid_count=' in script
    assert 'Calamares signing key has no usable user identity' in script
    assert 'actual_fingerprint == "$key_fingerprint"' in script
    assert 'calamares-release-key.json' in script
