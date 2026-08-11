#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path

def wait(path:Path,prefix:str,timeout:int):
    end=time.time()+timeout; seen=''
    while time.time()<end:
        if path.exists():
            seen=path.read_text(errors='replace')
            for line in seen.splitlines():
                if line.startswith(prefix): return json.loads(line[len(prefix):])
        time.sleep(1)
    raise TimeoutError(f'{prefix!r} not found in {path}; tail={seen[-2000:]}')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--log',type=Path,required=True); p.add_argument('--prefix',default='FELUNYX_EVIDENCE='); p.add_argument('--timeout',type=int,default=300); p.add_argument('--kernel',choices=['zen','lts']); p.add_argument('--live',choices=['true','false']); a=p.parse_args()
    data=wait(a.log,a.prefix,a.timeout)
    if a.kernel and data.get('kernel_variant')!=a.kernel: raise SystemExit(f'wrong kernel: {data}')
    if a.live and data.get('live')!=(a.live=='true'): raise SystemExit(f'wrong live state: {data}')
    if data.get('id')!='felunyx' or data.get('sshd_active'): raise SystemExit(f'invalid evidence: {data}')
    print(json.dumps(data,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
