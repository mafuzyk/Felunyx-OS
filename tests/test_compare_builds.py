import json,subprocess
from pathlib import Path

def test_comparator_distinguishes_r2_from_r3(tmp_path):
    a,b=tmp_path/'a',tmp_path/'b'; a.mkdir(); b.mkdir()
    for name in ('packages.txt','source-lock.json','validation-report.json'):
        (a/name).write_text(name); (b/name).write_text(name)
    (a/'a.iso').write_text('a'); (b/'b.iso').write_text('b')
    report=tmp_path/'report.json'; r=subprocess.run(['tools/felunyx-compare-builds',a,b,'--report',report])
    data=json.loads(report.read_text()); assert r.returncode==0; assert data['r2']=='pass'; assert data['r3']=='different'
