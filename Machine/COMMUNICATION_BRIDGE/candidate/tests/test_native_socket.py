import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import struct
import sys
import threading
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from machine import Rejected
from native_socket import NativeSocket, MAX_MESSAGE


def take(sock, size):
    data = b''
    while len(data) < size:
        part = sock.recv(size - len(data))
        if not part:
            raise AssertionError('Incomplete client frame')
        data += part
    return data


def client_message(sock):
    first, second = take(sock, 2)
    if not first & 128 or not second & 128:
        raise AssertionError('Expected a final masked client frame')
    size = second & 127
    if size == 126:
        size = struct.unpack('!H', take(sock, 2))[0]
    elif size == 127:
        size = struct.unpack('!Q', take(sock, 8))[0]
    mask = take(sock, 4)
    payload = take(sock, size)
    return json.loads(bytes(value ^ mask[index % 4] for index, value in enumerate(payload)))


def frame(payload, opcode=1, final=True):
    size = len(payload)
    length = (bytes([size]) if size < 126 else b'\x7e' + struct.pack('!H', size)
              if size < 65536 else b'\x7f' + struct.pack('!Q', size))
    return bytes([(128 if final else 0) | opcode]) + length + payload


class ConnectedSocket:
    def __init__(self, sock):
        self.sock = sock

    def connect(self, path):
        self.connected_path = path

    def __getattr__(self, key):
        return getattr(self.sock, key)


class NativeSocketTests(unittest.TestCase):
    def test_real_byte_stream_handshake_masking_fragmentation_and_rpc_identity(self):
        client, server = socket.socketpair()
        self.addCleanup(client.close)
        self.addCleanup(server.close)
        server.settimeout(3)
        received = []
        errors = []
        def serve():
            try:
                header = b''
                while b'\r\n\r\n' not in header:
                    header += server.recv(4096)
                key = next(line.split(': ', 1)[1] for line in header.decode().split('\r\n')
                           if line.startswith('Sec-WebSocket-Key:'))
                accept = base64.b64encode(hashlib.sha1(
                    (key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
                server.sendall(('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n'
                                'Connection: Upgrade\r\nSec-WebSocket-Accept: ' + accept + '\r\n\r\n').encode())
                request = client_message(server)
                received.append(request)
                server.sendall(frame(json.dumps({'id': request['id'], 'result': {}}).encode()))
                received.append(client_message(server))
                request = client_message(server)
                received.append(request)
                # An unrelated notification and response cannot satisfy the request.
                server.sendall(frame(b'{"method":"thread/changed","params":{}}'))
                server.sendall(frame(b'{"id":999,"result":{"wrong":true}}'))
                response = json.dumps({'id': request['id'], 'result': {'thread': {'id': 'fixture'}}}).encode()
                server.sendall(frame(response[:9], final=False) + frame(response[9:], opcode=0))
            except Exception as error:
                errors.append(error)
        worker = threading.Thread(target=serve)
        worker.start()
        info = types.SimpleNamespace(st_mode=stat.S_IFSOCK, st_uid=os.getuid())
        with patch.object(Path, 'stat', return_value=info), patch('native_socket.socket.socket',
                          return_value=ConnectedSocket(client)):
            with NativeSocket('unix:/private/tmp/fixture.sock', timeout=3) as native:
                result = native.request('thread/read', {'threadId': 'fixture', 'includeTurns': False})
        worker.join(timeout=4)
        self.assertFalse(worker.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(result, {'thread': {'id': 'fixture'}})
        self.assertEqual([message['method'] for message in received],
                         ['initialize', 'initialized', 'thread/read'])
        self.assertTrue(received[0]['params']['capabilities']['experimentalApi'])

    def stream(self, payload):
        client, server = socket.socketpair()
        self.addCleanup(client.close)
        self.addCleanup(server.close)
        native = NativeSocket('unix:/private/tmp/fixture.sock')
        native.socket = client
        import time
        native.deadline = time.monotonic() + 1
        server.sendall(payload)
        return native

    def test_oversized_frame_rejects_before_reading_payload(self):
        native = self.stream(b'\x81\x7f' + struct.pack('!Q', MAX_MESSAGE + 1))
        with self.assertRaises(Rejected):
            native._message()

    def test_masked_binary_and_invalid_continuation_reject(self):
        for payload in [b'\x81\x80', frame(b'{}', opcode=2), frame(b'{}', opcode=0)]:
            with self.subTest(payload=payload), self.assertRaises(Rejected):
                self.stream(payload)._message()

    def test_nonlocal_endpoints_and_execution_methods_reject(self):
        for endpoint in ['ws://localhost:4500', 'wss://remote', 'unix:relative']:
            with self.assertRaises(Rejected):
                NativeSocket(endpoint)
        native = NativeSocket('unix:/private/tmp/fixture.sock')
        for method in ['thread/start', 'thread/resume', 'turn/start', 'command/exec', 'thread/queue/delete']:
            with self.assertRaises(Rejected):
                native.request(method, {})

    def test_readonly_cli_entries_create_no_state(self):
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            root = str(Path(folder).resolve())
            cli = Path(__file__).resolve().parents[1] / 'src/machine.py'
            for args in [['work-view'], ['bridge-collect', '--id', 'missing'], ['--help']]:
                subprocess.run([sys.executable, str(cli), '--root', root, *args],
                               capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
            self.assertEqual(list(Path(root).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
