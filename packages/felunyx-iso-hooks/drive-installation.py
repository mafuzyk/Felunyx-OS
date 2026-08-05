#!/usr/bin/env python3
"""Semantic Calamares driver for disposable Phase 2 virtual disks."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import traceback
from pathlib import Path

import pyatspi

LOG = Path('/run/felunyx/installer-harness.log')
EVIDENCE_DIR = Path('/run/felunyx/installer-evidence')
DEBUG_LOG = Path('/run/felunyx/calamares-debug.log')
AUTOINSTALL_MARKER = Path(
    '/sys/firmware/qemu_fw_cfg/by_name/opt/felunyx/autoinstall/raw'
)
INSTALL_MODE_MARKER = Path(
    '/sys/firmware/qemu_fw_cfg/by_name/opt/felunyx/install-mode/raw'
)
FAILURE_SETTINGS = Path(
    '/usr/lib/felunyx/tests/calamares-failure/settings.conf'
)
VALID_MODES = {'success', 'failure'}
CALAMARES_LOGS = (
    Path('/root/.cache/calamares/session.log'),
    Path('/var/log/Calamares.log'),
)


def marker_value(path: Path) -> str:
    try:
        return path.read_bytes().rstrip(b'\0\n').decode('utf-8')
    except (OSError, UnicodeDecodeError):
        return ''


def fw_enabled() -> bool:
    return marker_value(AUTOINSTALL_MARKER) == '1'


def install_mode() -> str:
    mode = marker_value(INSTALL_MODE_MARKER)
    if mode not in VALID_MODES:
        raise RuntimeError(f'invalid or missing install mode: {mode!r}')
    return mode


def emit(event: str, **data: object) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {'event': event, **data}
    encoded = json.dumps(record, sort_keys=True)
    with LOG.open('a', encoding='utf-8') as handle:
        handle.write(encoded + '\n')
        handle.flush()
        os.fsync(handle.fileno())
    try:
        with open('/dev/ttyS0', 'w', encoding='utf-8') as handle:
            handle.write('FELUNYX_INSTALL=' + encoded + '\n')
    except OSError:
        pass


def preserve_logs() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    sources = (LOG, DEBUG_LOG, *CALAMARES_LOGS)
    for source in sources:
        if not source.is_file():
            continue
        destination = EVIDENCE_DIR / source.name
        if destination.exists() and destination.resolve() == source.resolve():
            continue
        shutil.copy2(source, destination)


def walk(node):
    yield node
    for child in node:
        yield from walk(child)


def desktop_nodes():
    for app in pyatspi.Registry.getDesktop(0):
        yield from walk(app)


def find(names, roles=None, timeout=60, process=None):
    deadline = time.monotonic() + timeout
    lowered = [value.casefold() for value in names]
    while time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            raise RuntimeError(
                f'Calamares exited unexpectedly with status {process.returncode}'
            )
        for node in desktop_nodes():
            name = (getattr(node, 'name', '') or '').casefold()
            role = node.getRoleName().casefold()
            if any(value in name for value in lowered) and (
                not roles or role in roles
            ):
                return node
        time.sleep(0.5)
    raise RuntimeError(f'accessibility object not found: {names}')


def click(*names, process=None):
    node = find(
        names,
        {'push button', 'radio button', 'check box'},
        process=process,
    )
    action = node.queryAction()
    for index in range(action.nActions):
        if action.getName(index) in ('click', 'press', 'activate', 'toggle'):
            action.doAction(index)
            return
    action.doAction(0)


def entries():
    result = []
    for node in desktop_nodes():
        if node.getRoleName().casefold() not in {'text', 'password text'}:
            continue
        try:
            node.queryEditableText()
            result.append(node)
        except Exception:
            continue
    return result


def set_entry(node, value):
    node.queryEditableText().setTextContents(value)


def start_calamares(mode: str):
    command = ['sudo', '-E', 'calamares', '-d']
    if mode == 'failure':
        command += ['-c', str(FAILURE_SETTINGS)]
    env = os.environ | {'QT_LINUX_ACCESSIBILITY_ALWAYS_ON': '1'}
    DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
    debug_handle = DEBUG_LOG.open('w', encoding='utf-8')
    process = subprocess.Popen(
        command,
        env=env,
        stdout=debug_handle,
        stderr=subprocess.STDOUT,
        text=True,
    )
    debug_handle.close()
    return process


def configure_install(process) -> None:
    find(['calamares', 'felunyx'], timeout=90, process=process)
    emit('stage', stage='installer-opened')

    for page in range(4):
        if page == 3:
            click('erase disk', 'erase', process=process)
        click('next', process=process)
        time.sleep(1)

    fields = entries()
    values = [
        'Felunyx Test',
        'felunyx',
        'felunyx-vm',
        'FelunyxPhase2!',
        'FelunyxPhase2!',
    ]
    if len(fields) < len(values):
        raise RuntimeError(
            f'expected at least {len(values)} editable fields, found {len(fields)}'
        )
    for node, value in zip(fields[-len(values):], values):
        set_entry(node, value)

    click('next', process=process)
    time.sleep(1)
    click('install', process=process)
    time.sleep(1)
    click('install now', 'continue', 'confirm', process=process)
    emit('stage', stage='installation-confirmed')


def wait_outcome(process, mode: str, timeout: int = 1800) -> str:
    deadline = time.monotonic() + timeout
    success_names = ('all done', 'finished', 'restart')
    failure_names = (
        'felunyxinjectedfailure',
        'intentional phase 2 installer failure injection',
    )

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f'Calamares exited unexpectedly with status {process.returncode}'
            )
        names = [
            (getattr(node, 'name', '') or '').casefold()
            for node in desktop_nodes()
        ]
        if any(
            expected in observed
            for observed in names
            for expected in success_names
        ):
            if mode == 'failure':
                raise RuntimeError('unexpected success in failure mode')
            return 'success'
        if any(
            expected in observed
            for observed in names
            for expected in failure_names
        ):
            if mode == 'success':
                raise RuntimeError('unexpected injected failure in success mode')
            return 'failure'
        time.sleep(0.5)
    raise RuntimeError(f'installer outcome was not observed for mode {mode}')


def poweroff() -> None:
    subprocess.run(['systemctl', 'poweroff'], check=False)


def main() -> int:
    if not fw_enabled():
        return 0

    mode = install_mode()
    emit('start', mode=mode)
    process = start_calamares(mode)
    configure_install(process)
    outcome = wait_outcome(process, mode)

    if outcome == 'failure':
        emit(
            'failure',
            stage='felunyx-fail',
            error_class='FelunyxInjectedFailure',
        )
    else:
        emit('success', mode=mode)

    preserve_logs()
    poweroff()
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        emit(
            'blocked',
            error=str(exc),
            traceback=traceback.format_exc(),
        )
        preserve_logs()
        poweroff()
        raise
