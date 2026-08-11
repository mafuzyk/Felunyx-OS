import json,subprocess
from pathlib import Path

def run(*a): return subprocess.run(['tools/sync-releng',*map(str,a)],text=True,capture_output=True)
def test_sync_detects_and_applies(tmp_path):
    src=tmp_path/'src'; dst=tmp_path/'dst'; src.mkdir(); dst.mkdir(); (src/'a').write_text('one'); (dst/'a').write_text('old'); report=tmp_path/'r.json'
    assert run('check','--source',src,'--target',dst,'--report',report).returncode==3
    assert json.loads(report.read_text())['modified']==['a']
    assert run('apply','--source',src,'--target',dst,'--report',report,'--yes').returncode==0
    assert (dst/'a').read_text()=='one'
    assert run('check','--source',src,'--target',dst,'--report',report).returncode==0
