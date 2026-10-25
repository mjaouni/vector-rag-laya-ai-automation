"""Conservative publication checks; report filenames, never matched credential text."""
import argparse
import os
from pathlib import Path
import re
import subprocess

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
SECRET = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|pypi-[A-Za-z0-9_-]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
PRIVATE_PATH = re.compile(rb'[A-Za-z]:[\\/]Users[\\/][^\s\\/]+')
EMAIL = re.compile(rb'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
MODEL_EXTENSIONS = {'.safetensors', '.gguf', '.pt', '.pth', '.bin', '.onnx'}


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged', action='store_true')
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    tokens = {dotenv_values(ROOT / '.env').get('WORKFLOW_TOKEN'), os.getenv('WORKFLOW_TOKEN')}
    tokens = [value.encode() for value in tokens if value and value != 'local-dev-only-change-me']
    objects = []
    if args.history:
        for commit in git('rev-list', '--all').decode().splitlines():
            for name in git('ls-tree', '-r', '--name-only', commit).decode().splitlines():
                objects.append((f'{commit[:8]}:{name}', name, git('show', f'{commit}:{name}')))
    else:
        options = ['ls-files', '--cached'] if args.staged else ['ls-files', '--cached', '--others', '--exclude-standard']
        for name in sorted(set(git(*options).decode().splitlines())):
            data = git('show', ':' + name) if args.staged else (ROOT / name).read_bytes()
            objects.append((name, name, data))
    issues = []
    for label, name, data in objects:
        if name == '.env' or any(name.startswith(p) for p in ('.venv/', 'data/', '.runtime/', '.n8n/', '.ollama/')):
            issues.append((label, 'private runtime path'))
        if Path(name).suffix in MODEL_EXTENSIONS or len(data) > 5_000_000:
            issues.append((label, 'model or unexpectedly large binary'))
        if Path(name).suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}:
            continue  # Screenshots require visual review, performed separately.
        if SECRET.search(data):
            issues.append((label, 'credential/private-key pattern'))
        if PRIVATE_PATH.search(data):
            issues.append((label, 'personal Windows path'))
        if any(token in data for token in tokens):
            issues.append((label, 'actual local workflow token'))
        for email in EMAIL.findall(data):
            if not email.lower().endswith((b'.test', b'@users.noreply.github.com')):
                issues.append((label, 'non-demo email address'))
    if issues:
        for label, reason in sorted(set(issues)):
            print(f'REVIEW {label}: {reason}')
        return 1
    print(f'Publication checks passed for {len(objects)} file versions; screenshots require separate visual review.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
