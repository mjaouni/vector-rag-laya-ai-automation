"""Internal launcher: record the real worker PID, including Windows venv launchers."""
import argparse
import hmac
import json
import os
from pathlib import Path
import secrets
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8003)
    args = parser.parse_args()
    runtime = ROOT / '.runtime'
    runtime.mkdir(exist_ok=True)
    stop_key = secrets.token_hex(24)
    signal_path = runtime / f'stop-{os.getpid()}.signal'
    (runtime / 'api.json').write_text(json.dumps({'pid': os.getpid(), 'port': args.port, 'stop_key': stop_key}), encoding='utf-8')
    import uvicorn
    server = uvicorn.Server(uvicorn.Config('api:app', host='0.0.0.0', port=args.port, timeout_graceful_shutdown=30))
    done = threading.Event()

    def watch_shutdown():
        while not done.wait(0.25):
            try:
                value = signal_path.read_text(encoding='utf-8-sig').strip()
            except OSError:
                continue
            if hmac.compare_digest(value, stop_key):
                server.should_exit = True
                return

    threading.Thread(target=watch_shutdown, daemon=True).start()
    try:
        server.run()
    finally:
        done.set()
        signal_path.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
