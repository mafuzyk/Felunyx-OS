from pathlib import Path


def test_release_key_import_validates_exact_certificate_identity_and_records_evidence():
    script = Path("tools/felunyx-build").read_text()

    assert "release_primary_fingerprint" in script
    assert "release_subkey_fingerprint" in script
    assert "--with-subkey-fingerprint" in script
    assert 'grep -Fxq "$release_primary_fingerprint"' in script
    assert 'grep -Fxq "$release_subkey_fingerprint"' in script
    assert "--keyserver" not in script
    assert "--recv-keys" not in script
    assert "import-options import-minimal" in script
    assert "uid_count=" in script
    assert "calamares-release-key.json" in script
    assert "https://github.com/adriaandegroot.gpg" not in script
