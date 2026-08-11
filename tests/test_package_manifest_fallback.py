from pathlib import Path


def test_build_uses_mkarchiso_resolved_package_manifest_with_fallback():
    script = Path('tools/felunyx-build').read_text()
    lookup = "manifest=$(find \"$work/archiso/iso\" -maxdepth 3 -type f -name 'pkglist.*.txt' -print -quit)"
    guard = 'if [[ -n $manifest ]]; then'
    resolved_copy = 'cp "$manifest" "$stage/packages.txt"'
    fallback = 'cp "$profile/packages.x86_64" "$stage/packages.txt"'
    assert lookup in script
    assert guard in script
    assert resolved_copy in script
    assert fallback in script
    assert script.index(lookup) < script.index(guard) < script.index(resolved_copy) < script.index(fallback)
    assert "if manifest=$(find" not in script
