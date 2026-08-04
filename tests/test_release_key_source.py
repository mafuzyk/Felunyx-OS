from pathlib import Path


def test_release_key_source_uses_signer_certificate_and_exact_primary_identity():
    script = Path('tools/felunyx-build').read_text()
    assert 'key_source=https://github.com/adriaandegroot.gpg' in script
    assert 'release_primary_fingerprint=00ACD15E25A79FEE028B0EE57FEA3DA6169C77D6' in script
    assert 'release_subkey_fingerprint=6D98B995A1CA6CE4BB906518C7AA337DFA13881E' in script
    assert '--with-subkey-fingerprint' in script
    assert 'grep -Fxq "$release_primary_fingerprint"' in script
    assert 'grep -Fxq "$release_subkey_fingerprint"' in script
    assert '--keyserver' not in script
    assert '--recv-keys' not in script
    assert 'import-options import-minimal' in script
    assert 'uid_count=' in script
    assert 'calamares-release-key.json' in script
