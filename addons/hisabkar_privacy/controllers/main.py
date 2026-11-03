import json
import logging
from collections import deque

from odoo import http
from odoo.http import request

from odoo.addons.html_editor.controllers.main import HTML_Editor

from ..models.ir_http import CSP_REPORT_PATH

_logger = logging.getLogger(__name__)

# Most recent violation reports, newest last; read by tests and support diagnostics.
csp_reports = deque(maxlen=200)
MAX_REPORT_BYTES = 16 * 1024


class CspReport(http.Controller):

    @http.route(CSP_REPORT_PATH, type='http', auth='none', methods=['POST'], csrf=False, save_session=False)
    def csp_report(self, **kwargs):
        """NFR-SEC-007: browsers report policy violations here, to our own server only.

        A violation means a screen tried to load or call something off our origin: either a bug in
        our UI or an attempted leak. Logged as a warning so it shows up in support logs.
        """
        body = request.httprequest.get_data(cache=False)[:MAX_REPORT_BYTES]
        try:
            report = json.loads(body or b'{}').get('csp-report', {})
        except ValueError:
            report = {}
        entry = {key: str(report.get(key, ''))[:500]
                 for key in ('document-uri', 'violated-directive', 'blocked-uri')}
        csp_reports.append(entry)
        _logger.warning("Content-Security-Policy violation: %s blocked %s on %s",
                        entry['violated-directive'], entry['blocked-uri'], entry['document-uri'])
        return request.make_response('', status=204)


class HtmlEditorNoLinkPreview(HTML_Editor):
    """NFR-SEC-006: upstream fetches any URL from the server to build a preview card, and the
    external route needs no login. No server-side fetching of user-supplied URLs."""

    @http.route()
    def link_preview_metadata(self, preview_url):
        return {}

    @http.route()
    def link_preview_metadata_internal(self, preview_url):
        return {}
