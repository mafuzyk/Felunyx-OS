import json,subprocess
from pathlib import Path

def test_validator_reports_missing_requirements(tmp_path):
    p=tmp_path/'profile'; p.mkdir(); (p/'packages.x86_64').write_text('linux-zen\n'); (p/'profiledef.sh').write_text('iso_name="bad"\n')
    report=tmp_path/'report.json'; r=subprocess.run(['tools/felunyx-validate','--profile',p,'--report',report])
    data=json.loads(report.read_text()); assert r.returncode==1; assert data['status']=='fail'
