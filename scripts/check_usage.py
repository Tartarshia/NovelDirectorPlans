"""Read the signed-in Codex five-hour quota without starting a model turn.

Exit codes: 0 = continue, 2 = pause (remaining < 15%), 3 = unknown.
Account quota receipts belong in the local reading workspace, never this repo.
Protocol: https://developers.openai.com/codex/app-server/
"""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time


def classify(result):
    buckets = result.get('rateLimitsByLimitId') or {}
    if 'codex' in buckets:
        buckets = {'codex': buckets['codex']}
    elif not buckets:
        single = result.get('rateLimits') or {}
        buckets = {single.get('limitId') or 'codex': single}
    windows = []
    for limit_id, bucket in buckets.items():
        if not isinstance(bucket, dict):
            continue
        for name in ('primary', 'secondary'):
            window = bucket.get(name)
            if not isinstance(window, dict) or window.get('windowDurationMins') != 300:
                continue
            used = window.get('usedPercent')
            if isinstance(used, bool) or not isinstance(used, (int, float)) or not math.isfinite(used) or used < 0:
                continue
            windows.append({'limit_id': limit_id, 'window': name,
                            'used_percent': used, 'remaining_percent': max(0, 100 - used),
                            'resets_at_unix': window.get('resetsAt')})
    if not windows:
        return {'decision': 'unknown', 'reason': 'no_valid_300_minute_quota_returned'}
    remaining = min(w['remaining_percent'] for w in windows)
    return {'decision': 'pause' if remaining < 15 else 'continue',
            'remaining_percent': remaining, 'threshold_percent': 15, 'windows': windows}


def read_limits(timeout=25):
    executable = shutil.which('codex')
    if not executable:
        raise RuntimeError('codex_executable_not_found')
    process = subprocess.Popen([executable, 'app-server', '--listen', 'stdio://'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, text=True, encoding='utf-8',
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    messages = queue.Queue()

    def receive():
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except json.JSONDecodeError:
                pass
        messages.put(None)

    threading.Thread(target=receive, daemon=True).start()
    deadline = time.monotonic() + timeout

    def send(message):
        process.stdin.write(json.dumps(message) + '\n')
        process.stdin.flush()

    def response(request_id):
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError('quota_read_timeout')
            try:
                message = messages.get(timeout=remaining)
            except queue.Empty:
                raise RuntimeError('quota_read_timeout') from None
            if message is None:
                raise RuntimeError('app_server_closed_before_quota_response')
            if message.get('id') == request_id:
                if 'error' in message:
                    raise RuntimeError('quota_protocol_request_failed')
                return message.get('result', {})

    try:
        send({'id': 1, 'method': 'initialize', 'params': {
            'clientInfo': {'name': 'novel_director_quota_check', 'version': '1.0.0'}}})
        response(1)
        send({'method': 'initialized', 'params': {}})
        send({'id': 2, 'method': 'account/rateLimits/read'})
        return response(2)
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, help='Optional LOCAL receipt outside the publishing repo')
    args = parser.parse_args()
    if args.record and args.record.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        parser.error('Account quota receipts must stay outside the publishing repo')
    try:
        report = classify(read_limits())
    except (RuntimeError, OSError) as exc:
        report = {'decision': 'unknown', 'reason': str(exc) if isinstance(exc, RuntimeError) else 'local_quota_read_failed'}
    report['checked_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    report['source'] = 'codex_app_server_account_rateLimits_read'
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.record.with_suffix(args.record.suffix + '.tmp')
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(args.record)
    print(json.dumps(report, ensure_ascii=False))
    return {'continue': 0, 'pause': 2, 'unknown': 3}[report['decision']]


if __name__ == '__main__':
    raise SystemExit(main())
