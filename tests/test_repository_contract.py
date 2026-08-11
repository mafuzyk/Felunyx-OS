from pathlib import Path

def test_core_scripts_are_strict():
    for p in Path('tools').glob('felunyx-*'):
        if p.read_text().startswith('#!/usr/bin/env bash'):
            assert 'set -Eeuo pipefail' in p.read_text(),p

def test_expected_roots_exist():
    for root in ('build','tools','tests','iso'):
        assert Path(root).exists()
