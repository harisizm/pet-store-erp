import base64
import json
import re
from unittest.mock import patch

from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger

from odoo.addons.hisabkar_privacy.controllers import main as controllers
from odoo.addons.hisabkar_privacy.models.ir_http import CSP_REPORT_PATH, merge_policy


@tagged('post_install', '-at_install', 'hisabkar_privacy')
class TestContentSecurityPolicy(HttpCase):
    """NFR-SEC-007: the browser is kept on our own origin."""

    def _policy(self, response):
        return response.headers.get('Content-Security-Policy', '')

    def assertContained(self, policy, own_host):
        self.assertIn("default-src 'self'", policy)
        self.assertIn("object-src 'none'", policy)
        hosts = set(re.findall(r'(?:https?|wss?)://([^\s;]+)', policy))
        self.assertEqual(hosts, {own_host}, f"policy allows outside hosts: {policy}")

    def test_policy_on_pages(self):
        response = self.url_open('/web/login')
        self.assertContained(self._policy(response), response.url.split('/')[2])

    def test_policy_on_error_pages(self):
        response = self.url_open('/hisabkar-no-such-page')
        self.assertEqual(response.status_code, 404)
        self.assertContained(self._policy(response), response.url.split('/')[2])

    def test_file_downloads_keep_stricter_upstream_policy(self):
        """Regression: merging used to add script-src to upstream's `default-src 'none'` on file
        streams, letting an uploaded HTML/SVG run inline script on our origin."""
        attachment = self.env['ir.attachment'].create({
            'name': 'page.html', 'mimetype': 'text/html', 'public': True,
            'datas': base64.b64encode(b'<script>alert(1)</script>'),
        })
        policy = self._policy(self.url_open(f'/web/content/{attachment.id}'))
        self.assertIn("default-src 'none'", policy)
        self.assertNotIn('unsafe-inline', policy)
        self.assertNotIn('script-src', policy)

    def test_merge_keeps_upstream_directives(self):
        merged = merge_policy("frame-ancestors 'none'", {'default-src': "'self'", 'frame-ancestors': "'self'"})
        self.assertEqual(merged, "frame-ancestors 'none'; default-src 'self'")

    def test_injected_host_header_cannot_add_directives(self):
        response = self.url_open('/web/login', headers={'Host': "evil.example; report-uri https://evil.example"})
        self.assertNotIn('evil.example', self._policy(response))

    @mute_logger(controllers._logger.name)
    def test_violation_reports_are_received_locally(self):
        with patch.object(controllers, 'csp_reports', controllers.csp_reports.__class__()) as reports:
            body = json.dumps({'csp-report': {'document-uri': 'http://x/odoo', 'violated-directive': 'img-src',
                                              'blocked-uri': 'https://www.gravatar.com/avatar/x'}})
            response = self.url_open(CSP_REPORT_PATH, data=body, headers={'Content-Type': 'application/csp-report'})
            self.assertEqual(response.status_code, 204)
            self.assertEqual(reports[-1]['blocked-uri'], 'https://www.gravatar.com/avatar/x')

    def test_back_office_loads_without_violations(self):
        """The real web client works under the policy: no console errors, no violation reports."""
        with patch.object(controllers, 'csp_reports', controllers.csp_reports.__class__()) as reports:
            # Give the browser a moment to deliver any violation report before checking.
            self.browser_js('/web', "setTimeout(() => console.log('test successful'), 1500)",
                            'odoo.isReady === true', login='admin')
            self.assertEqual(list(reports), [])
