from pathlib import Path

def test_installer_uses_accessibility_not_coordinates():
    text=Path('packages/felunyx-iso-hooks/drive-installation.py').read_text()
    assert 'pyatspi' in text
    for forbidden in ('xdotool','pyautogui','moveTo(','click('+'x='):
        assert forbidden not in text

def test_evidence_is_opt_in_and_serialized():
    text=Path('packages/felunyx-identity/felunyx-evidence').read_text()
    assert 'qemu_fw_cfg' in text and 'FELUNYX_EVIDENCE=' in text
    unit=Path('packages/felunyx-identity/felunyx-evidence.service').read_text()
    assert 'Type=oneshot' in unit

def test_grub_has_serial_and_stable_zen_default():
    text=Path('packages/felunyx-calamares-config/grub-default').read_text()
    assert 'GRUB_TOP_LEVEL=/boot/vmlinuz-linux-zen' in text
    assert 'console=ttyS0,115200n8' in text
