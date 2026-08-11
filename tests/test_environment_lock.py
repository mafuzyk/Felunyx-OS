import json,re
from pathlib import Path

def test_environment_is_immutable_and_locked():
    data=json.loads(Path('build/environment.lock.json').read_text())
    assert data['archiso']=='89-1'
    assert '@sha256:' in data['base_image']
    assert ':latest' not in data['base_image']
    assert re.search(r'@sha256:[0-9a-f]{64}$',data['base_image'])
    assert data['calamares']['version']=='3.3.14'
    assert len(data['calamares']['source_sha256'])==64
