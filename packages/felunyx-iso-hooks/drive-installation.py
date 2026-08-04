#!/usr/bin/env python3
"""Semantic Calamares driver for disposable Phase 2 virtual disks."""
from __future__ import annotations
import json, os, subprocess, time, traceback
from pathlib import Path
import pyatspi
LOG=Path('/run/felunyx/installer-harness.log')

def emit(event, **data):
    LOG.parent.mkdir(parents=True,exist_ok=True)
    record={'event':event,**data}
    with LOG.open('a') as f: f.write(json.dumps(record,sort_keys=True)+'\n')
    try:
        with open('/dev/ttyS0','w') as f: f.write('FELUNYX_INSTALL='+json.dumps(record,sort_keys=True)+'\n')
    except OSError: pass

def fw_enabled():
    p=Path('/sys/firmware/qemu_fw_cfg/by_name/opt/felunyx/autoinstall/raw')
    return p.exists() and p.read_bytes().rstrip(b'\0\n')==b'1'

def walk(node):
    yield node
    for child in node: yield from walk(child)

def find(names, roles=None, timeout=60):
    end=time.time()+timeout; lowered=[x.casefold() for x in names]
    while time.time()<end:
        for app in pyatspi.Registry.getDesktop(0):
            for node in walk(app):
                name=(getattr(node,'name','') or '').casefold()
                role=node.getRoleName().casefold()
                if any(x in name for x in lowered) and (not roles or role in roles): return node
        time.sleep(.5)
    raise RuntimeError(f'accessibility object not found: {names}')

def click(*names):
    node=find(names,{'push button','radio button','check box'})
    action=node.queryAction()
    for i in range(action.nActions):
        if action.getName(i) in ('click','press','activate','toggle'): action.doAction(i); return
    action.doAction(0)

def entries():
    out=[]
    for app in pyatspi.Registry.getDesktop(0):
        for node in walk(app):
            if node.getRoleName().casefold() in {'text','password text'}:
                try: node.queryEditableText(); out.append(node)
                except Exception: pass
    return out

def set_entry(node,value): node.queryEditableText().setTextContents(value)

def main():
    if not fw_enabled(): return 0
    emit('start')
    env=os.environ|{'QT_LINUX_ACCESSIBILITY_ALWAYS_ON':'1'}
    subprocess.Popen(['sudo','-E','calamares','-d'],env=env)
    find(['calamares','felunyx'],timeout=90)
    for page in range(4):
        if page==3: click('erase disk','erase')
        click('next'); time.sleep(1)
    fields=entries(); values=['Felunyx Test','felunyx','felunyx-vm','FelunyxPhase2!','FelunyxPhase2!']
    if len(fields)<len(values): raise RuntimeError(f'expected at least {len(values)} editable fields, found {len(fields)}')
    for node,value in zip(fields[-len(values):],values): set_entry(node,value)
    click('next'); time.sleep(1); click('install'); time.sleep(1); click('install now','continue','confirm')
    find(['all done','finished','restart'],timeout=1800)
    emit('success'); subprocess.run(['systemctl','poweroff'],check=False); return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as exc:
        emit('blocked',error=str(exc),traceback=traceback.format_exc()); raise
