import socket
from collections import deque
from contextlib import contextmanager
from unittest.mock import patch

from odoo.addons.hisabkar_privacy import egress

FAKE_IP = '203.0.113.10'  # TEST-NET-3: documentation range, never routed


class NetworkFence:
    """Stands in for the real resolver and connect() underneath the guard.

    Anything that gets past the guard lands here, is recorded and is refused, so a broken guard
    makes a test fail instead of reaching the internet during the test run. ``blocked`` is a fresh
    record of the guard's refusals for this fence only (the module-level record is bounded and
    shared, so length comparisons on it can pass falsely once it is full).
    """

    def __init__(self):
        self.lookups = []
        self.connects = []
        self.blocked = deque()
        self._real_getaddrinfo = egress._real_getaddrinfo

    def getaddrinfo(self, host, port, *args, **kwargs):
        name = host.decode() if isinstance(host, bytes) else str(host)
        if egress.is_loopback(name) or egress._as_ip(name) is not None:
            # No DNS query happens for these, so nothing can leave.
            return self._real_getaddrinfo(host, port, *args, **kwargs)
        self.lookups.append((name, port))
        return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', (FAKE_IP, port or 0))]

    def connect(self, sock, address):
        self.connects.append((address[0], address[1]))
        raise ConnectionRefusedError("NetworkFence: connection reached the network layer")

    def connect_ex(self, sock, address):
        self.connects.append((address[0], address[1]))
        return 111  # ECONNREFUSED

    @property
    def reached(self):
        return self.lookups + self.connects


@contextmanager
def network_fence():
    fence = NetworkFence()
    with patch.object(egress, '_real_getaddrinfo', fence.getaddrinfo), \
            patch.object(egress, '_real_connect', fence.connect), \
            patch.object(egress, '_real_connect_ex', fence.connect_ex), \
            patch.object(egress, 'blocked_attempts', fence.blocked):
        yield fence


class RealRequestsMixin:
    """The test framework blocks external HTTP itself, which would hide whether *our* guard works.

    Hand requests back to the real transport; the NetworkFence underneath the guard still keeps
    anything from leaving.
    """

    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        from odoo.tests.common import _super_send
        return _super_send(s, r, **kw)
