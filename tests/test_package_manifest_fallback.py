from pathlib import Path


def test_build_falls_back_when_mkarchiso_emits_no_external_package_manifest():
    script = Path('tools/felunyx-build').read_text()
    lookup = "manifest=$(find \"$out\" -maxdepth 1 -type f -name '*pkglist*.txt' -print -quit)"
    guard = 'if [[ -n $manifest ]]; then'
    fallback = 'cp "$profile/packages.x86_64" "$stage/packages.txt"'
    assert lookup in script
    assert guard in script
    assert fallback in script
    assert script.index(lookup) < script.index(guard) < script.index(fallback)
    assert "if manifest=$(find \"$out\"" not in script
