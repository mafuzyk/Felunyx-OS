import json
from pathlib import Path


PRIMARY_FINGERPRINT = "00ACD15E25A79FEE028B0EE57FEA3DA6169C77D6"
SIGNING_SUBKEY_FINGERPRINT = "6D98B995A1CA6CE4BB906518C7AA337DFA13881E"
MERGED_CERTIFICATE_SHA256 = "b3e5851676c35bc5506433ea77792e87594180581a420be9bdbc8d3f501c3789"
RELEASE_SIGNATURE_SHA256 = "1dcf71c518ca9a08f62ad6c6532001c46a72505bac7452e52c567cbd3021a076"


def test_calamares_pkgbuild_uses_the_published_asc_signature_and_primary_key():
    pkgbuild = Path("packages/calamares/PKGBUILD").read_text()

    assert "calamares-${pkgver}.tar.gz.asc" in pkgbuild
    assert "calamares-${pkgver}.tar.gz.sig" not in pkgbuild
    assert RELEASE_SIGNATURE_SHA256 in pkgbuild
    assert f"validpgpkeys=('{PRIMARY_FINGERPRINT}')" in pkgbuild
    assert SIGNING_SUBKEY_FINGERPRINT not in pkgbuild.split("validpgpkeys=", 1)[1]


def test_environment_lock_pins_the_vendored_release_certificate_and_provenance():
    lock = json.loads(Path("build/environment.lock.json").read_text())
    calamares = lock["calamares"]

    assert calamares["release_certificate_path"] == "keys/calamares/3.3.14-release-key.asc"
    assert calamares["release_certificate_sha256"] == MERGED_CERTIFICATE_SHA256
    assert calamares["release_signature_sha256"] == RELEASE_SIGNATURE_SHA256
    assert calamares["primary_key_fingerprint"] == PRIMARY_FINGERPRINT
    assert calamares["signing_subkey_fingerprint"] == SIGNING_SUBKEY_FINGERPRINT
    assert calamares["certificate_provenance"] == {
        "identity_source": "https://calamares.io/pk-7FEA3DA6169C77D6.txt",
        "identity_sha256": "46ed1304bf8db472de244a2647a3e04383753d5a3ccf55ce75660f7df0aee0b3",
        "technical_update_source": "https://keys.openpgp.org/vks/v1/by-fingerprint/6D98B995A1CA6CE4BB906518C7AA337DFA13881E",
        "technical_update_sha256": "86a20967e356756e7f19bdd24ef5d3b01a17e12c32d58400f9329ce004bc3cdf",
    }


def test_build_imports_only_the_hash_checked_vendored_certificate():
    script = Path("tools/felunyx-build").read_text()

    assert "release_certificate_path" in script
    assert "release_certificate_sha256" in script
    assert "sha256sum --check --strict" in script
    assert "curl --fail --location --silent --show-error \"$key_source\"" not in script
    assert "--keyserver" not in script
    assert "--recv-keys" not in script
