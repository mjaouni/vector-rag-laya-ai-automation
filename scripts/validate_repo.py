"""Offline repository checks; no models or services required."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    files = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    failures = []
    for name in sorted(set(files)):
        path = ROOT / name
        if not path.is_file():
            failures.append(f'Missing file: {name}')
            continue
        if path.stat().st_size > 5_000_000:
            failures.append(f'Unexpected large file: {name}')
        if path.suffix == '.py':
            ast.parse(path.read_text(encoding='utf-8-sig'), filename=name)
        if path.suffix in {'.yml', '.yaml'}:
            yaml.safe_load(path.read_text(encoding='utf-8'))
        if path.suffix != '.md':
            continue
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            target = target.split(' "', 1)[0].strip('<>')
            if urlsplit(target).scheme or target.startswith(('#', 'mailto:')):
                continue
            relative = unquote(target.split('#')[0])
            if relative and not (path.parent / relative).is_file():
                failures.append(f'Broken link in {name}: {target}')
    workflow = json.loads((ROOT / 'n8n/rag-laya-mailpit.json').read_text())
    nodes = {node['name']: node for node in workflow['nodes']}
    assert len(nodes) == 7 and not workflow['active']
    for source, ports in workflow['connections'].items():
        assert source in nodes
        for branch in ports['main']:
            for edge in branch:
                assert edge['node'] in nodes
    for node in nodes.values():
        assert 'credentials' not in node, 'Public export contains local credential references'
        if node['type'].endswith('httpRequest'):
            assert node['parameters']['genericAuthType'] == 'httpHeaderAuth'
            assert 'headerParameters' not in node['parameters']
    for name in files:
        if name == '.env' or any(name.startswith(prefix) for prefix in ('.venv/', 'data/', '.runtime/', '.n8n/', '.ollama/')):
            failures.append(f'Private/runtime file included: {name}')
    if failures:
        print('\n'.join(failures))
        return 1
    print(f'Validated {len(set(files))} files: syntax, YAML, relative Markdown links, n8n graph, size/runtime exclusions.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
