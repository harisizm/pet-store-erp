import re
from urllib.parse import urlsplit

from odoo import models
from odoo.http import request

CSP_REPORT_PATH = '/hisabkar/csp-report'
_SAFE_HOST = re.compile(r'^[A-Za-z0-9.\-]+(:\d+)?$|^\[[0-9A-Fa-f:.]+\](:\d+)?$')


def content_security_policy(host):
    """NFR-SEC-007: the browser may load and connect only to our own origin.

    'unsafe-inline' and 'unsafe-eval' are required by the web client (inline session bootstrap and
    runtime-compiled templates); they do not let the page reach any other host. The websocket is
    named explicitly because older Safari does not match ws/wss under 'self'. Violations are
    reported to our own server, never to a third party.
    """
    return {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval' blob:",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: blob:",
        'font-src': "'self' data:",
        'connect-src': f"'self' ws://{host} wss://{host}",
        'media-src': "'self' data: blob:",
        'frame-src': "'self' blob:",
        'worker-src': "'self' blob:",
        'manifest-src': "'self'",
        'object-src': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'",
        'frame-ancestors': "'self'",
        'report-uri': CSP_REPORT_PATH,
    }


def merge_policy(existing, ours):
    """Combine our policy with one upstream may already have set, never loosening upstream's.

    A policy with its own `default-src` (upstream sends `default-src 'none'` on every file download
    so an uploaded HTML/SVG cannot run script) is stricter than ours and is kept untouched: adding
    our script-src would override its default-src and re-enable inline script. A partial policy
    (the login page's lone `frame-ancestors 'self'`) keeps its directives and gets the rest of ours.
    """
    directives = {}
    for part in (existing or '').split(';'):
        name, _sep, value = part.strip().partition(' ')
        if name:
            directives[name.lower()] = value.strip()
    if 'default-src' in directives:
        return existing
    for name, value in ours.items():
        directives.setdefault(name, value)
    return '; '.join(f'{name} {value}' for name, value in directives.items())


def _policy_host():
    # The Host header is client-controlled and ends up inside a response header; anything that is
    # not a plain host[:port] falls back to the configured base URL so it cannot inject directives.
    host = request.httprequest.host
    if _SAFE_HOST.match(host or ''):
        return host
    base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
    return urlsplit(base_url).netloc or 'localhost'


def apply_policy(response):
    headers = getattr(response, 'headers', None)
    if headers is None:
        return response
    headers['Content-Security-Policy'] = merge_policy(
        headers.get('Content-Security-Policy'), content_security_policy(_policy_host()))
    return response


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _post_dispatch(cls, response):
        super()._post_dispatch(response)
        apply_policy(response)

    @classmethod
    def _handle_error(cls, exception):
        # Error pages (404, 403, 500) are documents too and must carry the policy (NFR-SEC-007).
        return apply_policy(super()._handle_error(exception))
