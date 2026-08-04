from pathlib import Path


def test_profile_includes_dependencies_for_enabled_archiso_pxe_hooks():
    packages = {
        line.strip()
        for line in Path('iso/profile/packages.x86_64').read_text().splitlines()
        if line.strip() and not line.lstrip().startswith('#')
    }
    assert {'mkinitcpio-nfs-utils', 'nbd'} <= packages


def test_validator_requires_enabled_archiso_pxe_dependencies():
    validator = Path('tools/felunyx-validate').read_text()
    assert '"mkinitcpio-nfs-utils"' in validator
    assert '"nbd"' in validator
