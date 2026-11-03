"""Process-wide outbound connection guard (ADR-0005, NFR-SEC-005, NFR-SEC-006).

This is the one sanctioned monkey-patch in Hisabkar (docs/AGENTS.md §1.9, docs/upstream-patches.md
row 1). It wraps ``socket.getaddrinfo`` and ``socket.socket.connect``/``connect_ex`` so that every
outbound connection made from Python, whatever library makes it (requests, urllib, smtplib, ...),
is checked before a single packet leaves:

* loopback is always allowed;
* the platform vendor's domains are always denied, even if someone allowlists them;
* anything else is allowed only if it matches ``hisabkar_egress_allowlist`` in the server config
  (comma-separated host names, ``*.suffix`` wildcards, IPs or CIDRs) or is the configured SMTP host.

Host names are checked at resolution, which keeps name-based decisions possible (connect() only
sees an IP). IP literals pass resolution untouched: resolving one sends nothing anywhere, and the
server must be able to resolve its own listen address (werkzeug looks up ``0.0.0.0`` to bind).
connect() then refuses any IP that is not local, allowlisted, or the result of an allowed lookup.

HTTP proxies are switched off for the process (``NO_PROXY=*``): through a proxy the guard would only
see the proxy's address, and a local proxy would pass as loopback while forwarding anywhere.

The database connection is not affected: psycopg2 talks to PostgreSQL through libpq, not Python
sockets. Known limits, covered by the network-layer firewall (ADR-0005 layer 5): code that bypasses
Python sockets (C extensions, subprocesses), ``socket.gethostbyname`` lookups, and UDP ``sendto``.
In gevent mode the framework patches ``socket`` at import, before this guard installs, so the guard
should wrap gevent's socket; not yet verified on the Linux SaaS host (P0-8).
"""
import fnmatch
import ipaddress
import logging
import os
import socket
import threading
import traceback
from collections import deque

from odoo.tools import config

_logger = logging.getLogger(__name__)

# Vendor endpoints found by the 2026-11-03 audit (ADR-0005). Denied unconditionally.
ALWAYS_DENY = (
    'odoo.com', '*.odoo.com',
    'odoo.sh', '*.odoo.sh',
    'odoocdn.com', '*.odoocdn.com',
)

# Most recent blocked attempts, newest last; read by tests and by support diagnostics.
blocked_attempts = deque(maxlen=200)

# The real implementations. Tests replace these to prove nothing reaches the network.
_real_getaddrinfo = socket.getaddrinfo
_real_connect = socket.socket.connect
_real_connect_ex = socket.socket.connect_ex

_resolved_ok = set()
_lock = threading.Lock()


class EgressBlocked(ConnectionRefusedError):
    """Raised instead of opening a connection the egress policy does not allow.

    A ConnectionRefusedError subclass, so callers that already handle network failures degrade
    gracefully instead of crashing.
    """


def _allowlist():
    entries = [e.strip().lower() for e in (config.get('hisabkar_egress_allowlist') or '').split(',')]
    smtp = (config.get('smtp_server') or '').strip().lower()
    if smtp and smtp != 'localhost':
        entries.append(smtp)
    return [e for e in entries if e]


def _as_ip(value):
    try:
        return ipaddress.ip_address(value.split('%', 1)[0])
    except ValueError:
        return None


def _matches(host, pattern):
    ip = _as_ip(host)
    if ip is not None and '/' in pattern:
        try:
            return ip in ipaddress.ip_network(pattern, strict=False)
        except ValueError:
            return False
    return fnmatch.fnmatchcase(host, pattern)


def is_always_denied(host):
    host = host.lower().rstrip('.')
    return any(fnmatch.fnmatchcase(host, pattern) for pattern in ALWAYS_DENY)


def is_loopback(host):
    """Loopback, or the unspecified address a server binds to (0.0.0.0 / ::)."""
    if host.lower() in ('localhost', 'localhost.localdomain'):
        return True
    ip = _as_ip(host)
    return ip is not None and (ip.is_loopback or ip.is_unspecified)


def is_allowed(host):
    host = host.lower().rstrip('.')
    if is_always_denied(host):
        return False
    if is_loopback(host):
        return True
    return any(_matches(host, pattern) for pattern in _allowlist())


def _block(host, port):
    caller = next(
        (f'{f.filename}:{f.lineno}' for f in reversed(traceback.extract_stack()[:-3])
         if 'hisabkar_privacy' not in f.filename and 'socket.py' not in f.filename),
        '?',
    )
    blocked_attempts.append((host, port, caller))
    _logger.warning("Blocked outbound connection to %s:%s from %s (ADR-0005)", host, port, caller)
    raise EgressBlocked(f"Connection to {host} is blocked by the privacy policy")


def _guarded_getaddrinfo(host, port, *args, **kwargs):
    if host is None:
        return _real_getaddrinfo(host, port, *args, **kwargs)
    name = host.decode() if isinstance(host, bytes) else str(host)
    if _as_ip(name) is not None:
        # A literal needs no lookup; connect() decides whether that IP may be reached.
        return _real_getaddrinfo(host, port, *args, **kwargs)
    if not is_allowed(name):
        _block(name, port)
    result = _real_getaddrinfo(host, port, *args, **kwargs)
    if not is_loopback(name):
        with _lock:
            _resolved_ok.update(info[4][0] for info in result)
    return result


def _check_address(sock, address):
    if sock.family not in (socket.AF_INET, socket.AF_INET6):
        return
    ip, port = address[0], address[1]
    if is_loopback(ip):
        return
    with _lock:
        resolved = ip in _resolved_ok
    if not resolved and not is_allowed(ip):
        _block(ip, port)


def _guarded_connect(sock, address):
    _check_address(sock, address)
    return _real_connect(sock, address)


def _guarded_connect_ex(sock, address):
    _check_address(sock, address)
    return _real_connect_ex(sock, address)


PROXY_VARIABLES = ('http_proxy', 'https_proxy', 'all_proxy', 'ftp_proxy')


def disable_proxies():
    """Make every HTTP client connect directly, so the guard judges the real destination.

    NO_PROXY=* also overrides proxies that requests/urllib pick up from the Windows registry.
    """
    for name in PROXY_VARIABLES:
        os.environ.pop(name, None)
        os.environ.pop(name.upper(), None)
    os.environ['NO_PROXY'] = os.environ['no_proxy'] = '*'


def install():
    """Install the guard. Idempotent; called when the module's Python package is imported."""
    disable_proxies()
    if socket.getaddrinfo is _guarded_getaddrinfo:
        return
    socket.getaddrinfo = _guarded_getaddrinfo
    socket.socket.connect = _guarded_connect
    socket.socket.connect_ex = _guarded_connect_ex
    _logger.info("Egress guard active (ADR-0005); allowlist: %s", _allowlist() or 'none')
