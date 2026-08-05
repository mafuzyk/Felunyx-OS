from __future__ import annotations

import importlib.util
from pathlib import Path

PRODUCTION = Path("packages/felunyx-calamares-config/settings.conf")
OVERLAY = Path("packages/felunyx-iso-hooks/calamares-failure")
FAILURE_SETTINGS = OVERLAY / "settings.conf"
FAILURE_MODULE = OVERLAY / "modules" / "felunyx-fail"
DRIVER = Path("packages/felunyx-iso-hooks/drive-installation.py")
PKGBUILD = Path("packages/felunyx-iso-hooks/PKGBUILD")


def exec_sequence(text: str) -> list[str]:
    line = next(
        item.strip()
        for item in text.splitlines()
        if item.strip().startswith("- exec:")
    )
    payload = line.split("[", 1)[1].rsplit("]", 1)[0]
    return [item.strip() for item in payload.split(",")]


def test_failure_overlay_inserts_one_module_without_changing_production():
    production = PRODUCTION.read_text(encoding="utf-8")
    failure = FAILURE_SETTINGS.read_text(encoding="utf-8")

    normal_exec = exec_sequence(production)
    failure_exec = exec_sequence(failure)
    position = normal_exec.index("bootloader") + 1
    expected = normal_exec.copy()
    expected.insert(position, "felunyx-fail")

    assert failure_exec == expected
    assert failure_exec[-1] == "umount"
    assert "/usr/lib/felunyx/tests/calamares-failure/modules" in failure
    assert "/usr/lib/calamares/modules" in failure
    for shared in (
        "show: [ welcome, locale, keyboard, partition, users, summary ]",
        "show: [ finished ]",
        "branding: felunyx",
        "prompt-install: true",
        "dont-chroot: false",
        "oem-setup: false",
    ):
        assert shared in production and shared in failure
    assert "felunyx-fail" not in production


def test_failure_module_has_explicit_python_job_contract():
    descriptor = (FAILURE_MODULE / "module.desc").read_text(
        encoding="utf-8"
    )
    for required in (
        "type: job",
        "name: felunyx-fail",
        "interface: python",
        "script: main.py",
        "noconfig: true",
    ):
        assert required in descriptor

    main_path = FAILURE_MODULE / "main.py"
    spec = importlib.util.spec_from_file_location("felunyx_fail", main_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.run() == (
        "FelunyxInjectedFailure",
        "Intentional Phase 2 installer failure injection",
    )


def test_failure_overlay_is_packaged_outside_production_config():
    text = PKGBUILD.read_text(encoding="utf-8")
    for source in (
        "calamares-failure/settings.conf",
        "calamares-failure/modules/felunyx-fail/module.desc",
        "calamares-failure/modules/felunyx-fail/main.py",
    ):
        assert source in text
    assert "/usr/lib/felunyx/tests/calamares-failure/settings.conf" in text
    assert (
        "/usr/lib/felunyx/tests/calamares-failure/modules/"
        "felunyx-fail/module.desc"
    ) in text
    assert (
        "/usr/lib/felunyx/tests/calamares-failure/modules/"
        "felunyx-fail/main.py"
    ) in text
    assert '"$pkgdir/etc/calamares/settings.conf"' not in text


def test_installer_driver_classifies_expected_failure_and_retains_logs():
    text = DRIVER.read_text(encoding="utf-8")
    for required in (
        "opt/felunyx/install-mode/raw",
        "{'success', 'failure'}",
        "/usr/lib/felunyx/tests/calamares-failure/settings.conf",
        "'-c'",
        "FelunyxInjectedFailure",
        "emit('failure'",
        "emit('blocked'",
        "/run/felunyx/installer-evidence",
        "/root/.cache/calamares/session.log",
        "/var/log/Calamares.log",
        "installer-harness.log",
    ):
        assert required in text

    assert "unexpected success in failure mode" in text
    assert "subprocess.Popen" in text
    assert "preserve_logs()" in text
    assert "systemctl" in text and "poweroff" in text


def test_failure_overlay_never_replaces_normal_settings():
    package = PKGBUILD.read_text(encoding="utf-8")
    driver = DRIVER.read_text(encoding="utf-8")
    assert "/etc/calamares/settings.conf" not in package
    assert "['sudo', '-E', 'calamares', '-d']" in driver
    assert "FAILURE_SETTINGS" in driver
