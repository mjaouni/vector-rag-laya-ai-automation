"""Read-only prerequisite checks; never opens embedded Qdrant."""
import argparse
import importlib.util
import json
from pathlib import Path
import socket
import sys
import urllib.request
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from service.config import settings  # noqa: E402


def http_check(name, url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = response.read(100000).decode()
        print(f"[OK] {name}: {url}")
        return True, json.loads(data) if data.startswith(('{', '[')) else None
    except (OSError, ValueError) as exc:
        print(f"[FAIL] {name}: {type(exc).__name__}")
        return False, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-model', action='store_true')
    args = parser.parse_args()
    required = sys.version_info >= (3, 12)
    print(f"Python {sys.version.split()[0]}; recommended: 3.12, 64-bit")
    modules = ['fastapi', 'uvicorn', 'qdrant_client', 'sentence_transformers']
    if settings.decision_provider == 'laya':
        modules.append('laya')
    for module in modules:
        found = importlib.util.find_spec(module) is not None
        print(f"[{'OK' if found else 'FAIL'}] Package: {module}")
        required &= found
    ok, tags = http_check('Ollama', settings.ollama_url + '/api/tags')
    models = [item.get('name', '') for item in (tags or {}).get('models', [])]
    installed = settings.ollama_model in models
    print(f"[{'OK' if installed else 'FAIL'}] Configured model installed: {settings.ollama_model}")
    required &= ok and installed
    http_check('n8n', 'http://localhost:5678/healthz')
    http_check('Mailpit UI', 'http://localhost:8025/api/v1/info')
    try:
        with socket.create_connection((settings.smtp_host, settings.smtp_port), timeout=5):
            print('[OK] SMTP reachable')
    except OSError as exc:
        print(f'[FAIL] SMTP: {type(exc).__name__}; check host port publishing')
    http_check('FastAPI (optional before start)', 'http://127.0.0.1:8003/healthz')
    print('Qdrant: not opened here. Stop API before scripts/seed.ps1.')
    print('Laya inference is not tested here. First request may download weights.')
    print('n8n must reach http://host.docker.internal:8003/healthz.')
    return 1 if args.require_model and not required else 0


if __name__ == '__main__':
    raise SystemExit(main())
