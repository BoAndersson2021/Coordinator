"""Supervised local diagnostics only. No project lifecycle or workflow effects."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.client import HTTPConnection
import hashlib
import hmac
import json
import os
from pathlib import Path
import plistlib
import secrets
import socket
import sqlite3
import subprocess
import sys
import threading
import time

import workflow_invariant as invariant
from machine import Ledger, Rejected, now, safe_regular

ASSETS = Path(__file__).with_name('dashboard_assets')
SOURCE = Path(__file__).resolve().parent
ROUTES = {'/': ('index.html', 'text/html; charset=utf-8'),
          '/dashboard.js': ('dashboard.js', 'text/javascript; charset=utf-8'),
          '/dashboard.css': ('dashboard.css', 'text/css; charset=utf-8')}
REFRESH_SECONDS = 2
STALE_SECONDS = 8


def profile():
    files = [*(SOURCE / name for name in invariant.SOURCE_MODULES),
             *(ASSETS / name for name, _ in ROUTES.values())]
    return hashlib.sha256(b''.join(safe_regular(p).read_bytes() for p in files)).hexdigest()


def snapshot(root):
    """Read through existing ledger integrity checks; never mutate or contact agents."""
    records = Ledger(root).status()
    tasks = []
    for task in records['tasks']:
        attempts = task.get('attempts', [])
        last = attempts[-1] if attempts else {}
        delivered = bool(last.get('receipt_digest'))
        reported = bool(task.get('report_digest'))
        reviewed = bool(task.get('review_digest'))
        tasks.append({'id': task['id'], 'project': task['project_id'], 'agent': task['agent_id'],
                      'thread_id': task.get('thread_id'), 'ledger_state': task['state'],
                      'version': task['version'], 'attempts': len(attempts),
                      'attempt_id': last.get('attempt_id'),
                      'delivery': 'Receipt retained; execution not established' if delivered else
                                  ('Attempt retained; delivery uncertain' if attempts else 'No delivery attempt'),
                      'receiver': 'Live execution not established', 'live_receiver_proven': False,
                      'report_retained': reported, 'review_retained': reviewed,
                      'historical_verdict': task.get('verdict') or
                          (task['state'] if task['state'] in ('verified', 'rejected') else None),
                      'evidence_at': task.get('updated_at') or task.get('prepared_at'),
                      'evidence_source': 'Integrity-checked local ledger; not a live agent observation',
                      'workflow_ready': False})
    return {'schema_version': 1, 'observed_at': now(), 'observation_scope': 'local_ledger_only',
            'network_observation': False, 'ledger_status': records['status'],
            'workflow_invariant': invariant.assessment(operation='dashboard-observation'),
            'tasks': tasks, 'counts': {'tasks': len(tasks), 'live_receivers_proven': 0,
                                     'reports_retained': sum(t['report_retained'] for t in tasks),
                                     'reviews_retained': sum(t['review_retained'] for t in tasks)},
            'refresh_seconds': REFRESH_SECONDS, 'stale_seconds': STALE_SECONDS}


class DashboardServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 16

    def __init__(self, root, port, token):
        self.root = Path(root).resolve()
        self.token = token
        self.started_at = now()
        self.instance = secrets.token_hex(16)
        self.source_profile = profile()
        self.snapshot_lock = threading.Lock()
        self.cached = None
        self.cached_at = 0
        super().__init__(('127.0.0.1', port), DashboardHandler)

    def health(self):
        return {'service': 'machine.dashboard', 'root': str(self.root),
                'pid': os.getpid(), 'instance': self.instance, 'started_at': self.started_at,
                'source_profile': self.source_profile, 'workflow_ready': False,
                'supervisor': 'launchd' if os.environ.get('MACHINE_DASHBOARD_SUPERVISED') == '1'
                              else 'test_or_unmanaged'}

    def observation(self):
        with self.snapshot_lock:
            if self.cached is None or time.monotonic() - self.cached_at >= REFRESH_SECONDS:
                self.cached = snapshot(self.root)
                self.cached_at = time.monotonic()
            return {**self.cached, 'service': self.health()}


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = 'MachineDashboard/1'
    sys_version = ''

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *_args):
        # Never log URLs, browser fragments, headers, tokens or report contents.
        pass

    def respond(self, code, data, content_type='application/json; charset=utf-8'):
        if not isinstance(data, bytes):
            data = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; "
                         "style-src 'self'; connect-src 'self'; img-src 'self'; "
                         "frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        authority = '127.0.0.1:' + str(self.server.server_port)
        if (self.headers.get('Host') != authority or
                self.headers.get('Origin', 'http://' + authority) != 'http://' + authority or
                self.headers.get('Sec-Fetch-Site') == 'cross-site'):
            return self.respond(403, {'status': 'local_origin_required'})
        if self.path in ROUTES:
            name, mime = ROUTES[self.path]
            return self.respond(200, safe_regular(ASSETS / name).read_bytes(), mime)
        if self.path not in ('/api/health', '/api/snapshot'):
            return self.respond(404, {'status': 'not_found'})
        token = self.headers.get('X-Machine-Token', '')
        if not hmac.compare_digest(token.encode(), self.server.token.encode()):
            return self.respond(401, {'status': 'dashboard_token_required'})
        try:
            if profile() != self.server.source_profile:
                raise Rejected('Dashboard source changed; supervisor is replacing this process')
            body = self.server.health() if self.path == '/api/health' else self.server.observation()
            self.respond(200, body)
        except (Rejected, OSError, ValueError, KeyError, TypeError, sqlite3.Error) as error:
            print(json.dumps({'service': 'machine.dashboard', 'status': 'observation_failed',
                              'error': type(error).__name__, 'at': now()}), file=sys.stderr, flush=True)
            self.respond(503, {'status': 'observation_failed', 'reason': str(error),
                              'workflow_invariant': invariant.assessment(operation='dashboard-observation')})

    def do_POST(self):
        self.respond(405, {'status': 'read_only_dashboard', 'workflow_ready': False})

    do_PUT = do_POST
    do_PATCH = do_POST
    do_DELETE = do_POST


def service_paths(root):
    identity = hashlib.sha256(str(Path(root).resolve()).encode()).hexdigest()[:16]
    home = Path.home().resolve()
    label = 'com.mammuth.machine.dashboard.' + identity
    return {'label': label, 'target': 'gui/' + str(os.getuid()) + '/' + label,
            'domain': 'gui/' + str(os.getuid()),
            'directory': home / 'Library/Application Support/MammuthMachine' / identity,
            'plist': home / 'Library/LaunchAgents' / (label + '.plist'),
            'log': home / 'Library/Logs/MammuthMachine' / (identity + '.log')}


def private_directory(path):
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise Rejected('Dashboard service directory must not be redirected')
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.stat().st_uid != os.getuid():
        raise Rejected('Dashboard service directory has a different owner')
    path.chmod(0o700)


def private_write(path, content):
    # Exclusive creation, no redirection/overwrite of someone else's service file.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def load_configuration(root):
    paths = service_paths(root)
    path = paths['directory'] / 'service.json'
    safe_regular(path)
    if path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
        raise Rejected('Dashboard configuration must be private and owned by this user')
    config = json.loads(path.read_text())
    if (set(config) != {'root', 'port', 'token', 'schema_version'} or config['schema_version'] != 1
            or config['root'] != str(Path(root).resolve()) or type(config['port']) is not int
            or not 1024 <= config['port'] <= 65535 or not isinstance(config['token'], str)
            or len(config['token']) != 64):
        raise Rejected('Dashboard service identity/configuration mismatch')
    return config


def launchctl(*args, check=True):
    try:
        result = subprocess.run(['/bin/launchctl', *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        raise Rejected('Dashboard supervisor command failed or timed out; no manual fallback')
    if check and result.returncode:
        raise Rejected('Dashboard supervisor failed: ' + result.stderr.strip()[:500])
    return result


def health_request(config):
    connection = HTTPConnection('127.0.0.1', config['port'], timeout=1)
    try:
        connection.request('GET', '/api/health', headers={'X-Machine-Token': config['token']})
        response = connection.getresponse()
        if response.status != 200:
            raise Rejected('Dashboard health did not return an authenticated observation')
        body = json.loads(response.read(65536))
    finally:
        connection.close()
    if (body.get('service') != 'machine.dashboard' or body.get('root') != config['root']
            or body.get('source_profile') != profile() or body.get('supervisor') != 'launchd'
            or body.get('workflow_ready') is not False):
        raise Rejected('Dashboard did not establish its exact supervised service identity')
    return body


def ensure_service(root, port=8765):
    """Idempotently adopt only our exact read-only service; no terminal or generic shell."""
    if sys.platform != 'darwin':
        raise Rejected('Automatic dashboard supervision requires macOS launchd; no manual fallback')
    if type(port) is not int or not 1024 <= port <= 65535:
        raise Rejected('Dashboard port must be between 1024 and 65535')
    root = Path(root).resolve()
    paths = service_paths(root)
    private_directory(paths['directory'])
    private_directory(paths['log'].parent)
    # LaunchAgents is shared with other applications: never change its mode.
    if any(p.is_symlink() for p in (paths['plist'].parent, *paths['plist'].parent.parents)):
        raise Rejected('Dashboard LaunchAgents path must not be redirected')
    paths['plist'].parent.mkdir(parents=True, exist_ok=True)
    config_path = paths['directory'] / 'service.json'
    if not config_path.exists():
        try:
            private_write(config_path, json.dumps({'schema_version': 1, 'root': str(root),
                          'port': port, 'token': secrets.token_hex(32)}).encode())
        except FileExistsError:
            pass  # A concurrent identical start won the exclusive creation.
    config = load_configuration(root)
    if config['port'] != port:
        raise Rejected('Dashboard already configured on port ' + str(config['port']))
    definition = {'Label': paths['label'], 'ProgramArguments': [sys.executable, '-B',
                  str(SOURCE / 'machine.py'), '--root', str(root), 'dashboard-serve'],
                  'RunAtLoad': True, 'KeepAlive': True, 'ThrottleInterval': 2,
                  'ProcessType': 'Background', 'WorkingDirectory': str(root),
                  'EnvironmentVariables': {'PYTHONDONTWRITEBYTECODE': '1',
                                           'MACHINE_DASHBOARD_SUPERVISED': '1'},
                  'StandardOutPath': str(paths['log']), 'StandardErrorPath': str(paths['log'])}
    if paths['plist'].exists():
        if paths['plist'].stat().st_uid != os.getuid() or paths['plist'].stat().st_mode & 0o077:
            raise Rejected('Dashboard supervisor definition must be private and owned by this user')
        if plistlib.loads(safe_regular(paths['plist']).read_bytes()) != definition:
            raise Rejected('Existing dashboard supervisor definition differs; adoption required')
    else:
        private_write(paths['plist'], plistlib.dumps(definition))
    loaded = launchctl('print', paths['target'], check=False)
    if loaded.returncode:
        # Fail loudly for occupied ports rather than attach to an unrelated server.
        with socket.socket() as probe:
            try:
                probe.bind(('127.0.0.1', port))
            except OSError:
                raise Rejected('Dashboard port is occupied; no unrelated service will be adopted')
        launched = launchctl('bootstrap', paths['domain'], str(paths['plist']), check=False)
        if launched.returncode and launchctl('print', paths['target'], check=False).returncode:
            raise Rejected('Dashboard supervisor bootstrap failed: ' + launched.stderr.strip()[:500])
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        try:
            health = health_request(config)
            actual = launchctl('print', paths['target'])
            if 'pid = ' + str(health['pid']) not in actual.stdout:
                raise Rejected('Dashboard process does not match its supervisor')
            url = 'http://127.0.0.1:' + str(port) + '/#token=' + config['token']
            try:
                opened = subprocess.run(['/usr/bin/open', url], capture_output=True, text=True, timeout=10)
            except (OSError, subprocess.SubprocessError):
                raise Rejected('Dashboard service is running but automatic browser opening failed or timed out')
            if opened.returncode:
                raise Rejected('Dashboard service is running but automatic browser opening failed')
            return {'status': 'dashboard_running', 'url': 'http://127.0.0.1:' + str(port) + '/',
                    'browser_opened': True, 'supervision': 'launchd KeepAlive + RunAtLoad',
                    'service': health, 'log': str(paths['log']), 'workflow_ready': False}
        except (TimeoutError, ConnectionError, OSError, ValueError):
            time.sleep(0.25)
    raise Rejected('Dashboard failed to become healthy within 15 seconds; see ' + str(paths['log']))


def serve(root):
    config = load_configuration(root)
    server = DashboardServer(root, config['port'], config['token'])
    print(json.dumps({'status': 'dashboard_listening', **server.health(),
                      'workflow_invariant': invariant.assessment(operation='dashboard-serve')}), flush=True)

    def watch_source():
        while True:
            time.sleep(1)
            try:
                if profile() == server.source_profile:
                    continue
            except (OSError, Rejected):
                pass
            print(json.dumps({'status': 'dashboard_source_changed', 'action': 'automatic_supervisor_restart',
                              'at': now()}), file=sys.stderr, flush=True)
            os._exit(75)

    threading.Thread(target=watch_source, daemon=True).start()
    try:
        server.serve_forever(poll_interval=0.25)
    finally:
        server.server_close()
