import json,os,subprocess
from pathlib import Path

def test_dry_run_materializes_both_modes(tmp_path):
    env=os.environ|{'FELUNYX_TMP_ROOT':str(tmp_path/'tmp'),'SOURCE_DATE_EPOCH':'1785734400'}
    for mode,args in [('integration',[]),('frozen',['--archive-date','2026/07/27'])]:
        out=tmp_path/mode
        r=subprocess.run(['tools/felunyx-build','--mode',mode,'--output',out,'--dry-run',*args],env=env,text=True,capture_output=True)
        assert r.returncode==0,r.stderr
        data=json.loads((out/'build-plan.json').read_text())
        assert data['mode']==mode

def test_frozen_requires_date(tmp_path):
    r=subprocess.run(['tools/felunyx-build','--mode','frozen','--output',tmp_path/'x','--dry-run'],text=True,capture_output=True)
    assert r.returncode!=0
