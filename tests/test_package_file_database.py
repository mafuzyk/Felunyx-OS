from pathlib import Path


def test_build_refreshes_file_databases_before_package_ownership_validation():
    script = Path('tools/felunyx-build').read_text()
    refresh = '"$pacman_wrapper" --files --refresh --noconfirm'
    validate = '"$ROOT/tools/felunyx-validate" --profile "$profile"'
    assert refresh in script
    assert script.index(refresh) < script.index(validate)
