import re
from pathlib import Path

OFFICIAL_OWNERS = {
    '/usr/lib/os-release': 'filesystem',
    '/usr/share/applications/calamares.desktop': 'calamares',
    '/etc/default/grub': 'grub',
}

def package_name(text: str) -> str:
    match = re.search(r'^pkgname=([^\n]+)$', text, re.MULTILINE)
    assert match
    return match.group(1).strip("'\"")

def literal_destinations(text: str) -> set[str]:
    return set(re.findall(r'"\$pkgdir([^"\n]+)"', text))

def test_locked_upstream_paths_have_one_package_owner():
    claims: dict[str, list[str]] = {path: [] for path in OFFICIAL_OWNERS}
    for recipe in Path('packages').glob('*/PKGBUILD'):
        text = recipe.read_text()
        name = package_name(text)
        for destination in literal_destinations(text):
            if destination in claims:
                claims[destination].append(name)
    assert claims['/usr/lib/os-release'] == []
    assert claims['/etc/default/grub'] == []
    assert claims['/usr/share/applications/calamares.desktop'] == ['calamares']

def test_customizations_live_in_package_owned_paths():
    identity = literal_destinations(Path('packages/felunyx-identity/PKGBUILD').read_text())
    installer = literal_destinations(Path('packages/felunyx-calamares-config/PKGBUILD').read_text())
    assert '/usr/lib/felunyx/os-release' in identity
    assert '/etc/calamares/preinstall_copy/etc/default/grub' in installer
