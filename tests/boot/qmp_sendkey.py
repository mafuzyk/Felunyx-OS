#!/usr/bin/env python3
import argparse,json,os,socket,time
p=argparse.ArgumentParser(); p.add_argument('--socket',required=True); p.add_argument('keys',nargs='+'); a=p.parse_args()
end=time.time()+30
while not os.path.exists(a.socket) and time.time()<end: time.sleep(.1)
s=socket.socket(socket.AF_UNIX); s.connect(a.socket); f=s.makefile('rwb',buffering=0)
f.readline(); f.write(json.dumps({'execute':'qmp_capabilities'}).encode()+b'\n'); f.readline()
for key in a.keys:
    cmd={'execute':'human-monitor-command','arguments':{'command-line':f'sendkey {key}'}}
    f.write(json.dumps(cmd).encode()+b'\n'); f.readline(); time.sleep(.2)
