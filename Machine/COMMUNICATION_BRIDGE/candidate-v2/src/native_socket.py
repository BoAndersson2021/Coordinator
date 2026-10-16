"""Bounded WebSocket JSON-RPC over an existing local Unix socket only."""
import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import struct
import time

from machine import Rejected

MAX_MESSAGE = 8 * 1024 * 1024
METHODS = {'thread/read', 'thread/turns/list', 'thread/items/list',
           'thread/queue/add', 'thread/queue/list'}


class NativeSocket:
    def __init__(self, endpoint, timeout=10):
        if not isinstance(endpoint, str) or not endpoint.startswith('unix:/'):
            raise Rejected('Bridge accepts only an explicitly bound local Unix socket')
        self.path = Path(endpoint[5:])
        self.timeout = timeout
        self.socket = None
        self.sequence = 0
        self.buffer = b''

    def __enter__(self):
        try:
            info = self.path.stat()
            if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid():
                raise Rejected('Native endpoint is not a socket owned by this user')
            self.deadline = time.monotonic() + self.timeout
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect(str(self.path))
            key = base64.b64encode(os.urandom(16)).decode()
            handshake = ('GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\n'
                         'Connection: Upgrade\r\nSec-WebSocket-Version: 13\r\n'
                         'Sec-WebSocket-Key: ' + key + '\r\n\r\n')
            self.socket.sendall(handshake.encode())
            while b'\r\n\r\n' not in self.buffer:
                self._receive()
                if len(self.buffer) > 16384:
                    raise Rejected('Native WebSocket handshake exceeds bound')
            header, self.buffer = self.buffer.split(b'\r\n\r\n', 1)
            lines = header.decode('ascii').split('\r\n')
            headers = {key.lower(): value for key, value in
                       (line.split(':', 1) for line in lines[1:])}
            expected = base64.b64encode(hashlib.sha1(
                (key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            if (lines[0].split()[1] != '101' or headers.get('sec-websocket-accept', '').strip() != expected
                    or headers.get('upgrade', '').strip().lower() != 'websocket'):
                raise Rejected('Native WebSocket handshake rejected')
            self._request('initialize', {'clientInfo': {'name': 'mammuth-machine',
                          'title': 'Mammuth Machine', 'version': '0.1'},
                          'capabilities': {'experimentalApi': True}})
            self._send(json.dumps({'method': 'initialized', 'params': {}}).encode())
            return self
        except Exception:
            self.close()
            raise

    def close(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def __exit__(self, *_):
        self.close()

    def _receive(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise Rejected('Native request deadline exceeded')
        self.socket.settimeout(remaining)
        part = self.socket.recv(65536)
        if not part:
            raise Rejected('Native socket closed before a complete response')
        self.buffer += part

    def _take(self, size):
        if size > MAX_MESSAGE:
            raise Rejected('Native response exceeds message bound')
        while len(self.buffer) < size:
            self._receive()
        result, self.buffer = self.buffer[:size], self.buffer[size:]
        return result

    def _send(self, payload, opcode=1):
        if len(payload) > MAX_MESSAGE:
            raise Rejected('Native request exceeds message bound')
        mask = os.urandom(4)
        size = len(payload)
        length = (bytes([size | 128]) if size < 126 else
                  b'\xfe' + struct.pack('!H', size) if size < 65536 else
                  b'\xff' + struct.pack('!Q', size))
        self.socket.sendall(bytes([128 | opcode]) + length + mask +
                            bytes(value ^ mask[index % 4] for index, value in enumerate(payload)))

    def _message(self):
        data = bytearray()
        started = False
        while True:
            first, second = self._take(2)
            opcode = first & 15
            if first & 112 or second & 128:
                raise Rejected('Unsupported native WebSocket frame')
            size = second & 127
            if size == 126:
                size = struct.unpack('!H', self._take(2))[0]
            elif size == 127:
                size = struct.unpack('!Q', self._take(8))[0]
            if len(data) + size > MAX_MESSAGE:
                raise Rejected('Native response exceeds message bound')
            payload = self._take(size)
            if opcode == 8:
                raise Rejected('Native WebSocket closed')
            if opcode in (9, 10):
                if size > 125 or not first & 128:
                    raise Rejected('Invalid native control frame')
                if opcode == 9:
                    self._send(payload, 10)
                continue
            if opcode not in (0, 1) or (opcode == 0) != started:
                raise Rejected('Invalid native message continuation')
            started = True
            data.extend(payload)
            if first & 128:
                return json.loads(data)

    def request(self, method, params):
        if method not in METHODS:
            raise Rejected('Unsupported native bridge method')
        return self._request(method, params)

    def _request(self, method, params):
        self.deadline = time.monotonic() + self.timeout
        self.sequence += 1
        request_id = self.sequence
        self._send(json.dumps({'id': request_id, 'method': method, 'params': params}).encode())
        for _ in range(1000):
            message = self._message()
            if not isinstance(message, dict):
                raise Rejected('Malformed native RPC response')
            if message.get('id') != request_id:
                continue
            if 'error' in message:
                raise Rejected('Native method rejected: ' + method)
            if not isinstance(message.get('result'), dict):
                raise Rejected('Missing native RPC result')
            return message['result']
        raise Rejected('Native notification bound exceeded')
