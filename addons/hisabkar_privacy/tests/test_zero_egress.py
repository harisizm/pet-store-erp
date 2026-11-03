import logging
import os
import socket
from unittest.mock import patch

import requests

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged
from odoo.tools import config, mute_logger

from odoo.addons.base.models import ir_cron
from odoo.addons.hisabkar_privacy import egress
from odoo.addons.hisabkar_privacy.models.hisabkar_privacy import DEAD_ENDPOINT, ENDPOINT_PARAMS
from odoo.addons.hisabkar_privacy.models.ir_module import is_blocked_name

from .common import FAKE_IP, RealRequestsMixin, network_fence

GUARD_LOGGER = egress._logger.name
VENDOR_HOSTS = ('odoo.com', 'services.odoo.com', 'iap.odoo.com', 'media-api.odoo.com',
                'iap-services.odoo.com', 'apps.odoo.com')


@tagged('post_install', '-at_install', 'hisabkar_privacy')
class TestEgressGuard(RealRequestsMixin, TransactionCase):
    """NFR-SEC-005, NFR-SEC-006: the guard decides before anything reaches the network."""

    @mute_logger(GUARD_LOGGER)
    def test_vendor_domains_denied_even_when_allowlisted(self):
        """NFR-SEC-005: the vendor's domains cannot be opened by configuration."""
        with network_fence() as fence, \
                patch.dict(config.options, {'hisabkar_egress_allowlist': 'odoo.com,*.odoo.com,services.odoo.com'}):
            for host in VENDOR_HOSTS:
                with self.subTest(host=host), self.assertRaises(egress.EgressBlocked):
                    socket.getaddrinfo(host, 443)
        self.assertEqual([attempt[0] for attempt in fence.blocked], list(VENDOR_HOSTS))
        self.assertEqual(fence.reached, [])

    @mute_logger(GUARD_LOGGER)
    def test_unlisted_host_and_raw_ip_denied(self):
        """NFR-SEC-006: default deny, by name and by raw IP."""
        with network_fence() as fence, patch.dict(config.options, {'hisabkar_egress_allowlist': ''}):
            with self.assertRaises(egress.EgressBlocked):
                socket.getaddrinfo('example.org', 443)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock, \
                    self.assertRaises(egress.EgressBlocked):
                sock.connect(('198.51.100.7', 80))
        self.assertEqual(len(fence.blocked), 2)
        self.assertEqual(fence.reached, [])

    def test_allowlisted_host_passes_guard(self):
        """NFR-SEC-006: an allowlisted integration host gets through the guard (and only it)."""
        with network_fence() as fence, \
                patch.dict(config.options, {'hisabkar_egress_allowlist': 'graph.facebook.com'}):
            infos = socket.getaddrinfo('graph.facebook.com', 443, type=socket.SOCK_STREAM)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock, \
                    self.assertRaises(ConnectionRefusedError) as caught:
                sock.connect(infos[0][4])
        self.assertNotIsInstance(caught.exception, egress.EgressBlocked)
        self.assertEqual(fence.lookups, [('graph.facebook.com', 443)])
        self.assertEqual(fence.connects, [(FAKE_IP, 443)])
        self.assertFalse(fence.blocked)

    def test_loopback_always_allowed(self):
        """Local services (the server itself, report rendering) are never blocked."""
        with network_fence() as fence:
            self.assertTrue(socket.getaddrinfo('localhost', 8069))
            self.assertTrue(socket.getaddrinfo('127.0.0.1', 8069))
        self.assertEqual(fence.reached, [])
        self.assertFalse(fence.blocked)

    @mute_logger(GUARD_LOGGER)
    def test_server_can_resolve_its_listen_address(self):
        """Regression: werkzeug resolves 0.0.0.0 (or a LAN interface IP) to bind the HTTP server.

        Resolving a literal must pass, without making that IP connectable.
        """
        with network_fence() as fence, patch.dict(config.options, {'hisabkar_egress_allowlist': ''}):
            self.assertTrue(socket.getaddrinfo('0.0.0.0', 8069, socket.AF_INET, socket.SOCK_STREAM))
            self.assertTrue(socket.getaddrinfo('192.0.2.5', 8069, socket.AF_INET, socket.SOCK_STREAM))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock, \
                    self.assertRaises(egress.EgressBlocked):
                sock.connect(('192.0.2.5', 8069))
        self.assertEqual(fence.reached, [])

    @mute_logger(GUARD_LOGGER)
    def test_requests_library_blocked_end_to_end(self):
        """NFR-SEC-005: a real `requests` call to the vendor fails inside our own process."""
        with network_fence() as fence:
            with self.assertRaises(requests.exceptions.ConnectionError):
                requests.post('https://services.odoo.com/publisher-warranty/', data={'x': 1}, timeout=5)
        self.assertEqual([attempt[0] for attempt in fence.blocked], ['services.odoo.com'])
        self.assertEqual(fence.reached, [])

    @mute_logger(GUARD_LOGGER)
    def test_proxies_cannot_route_around_the_guard(self):
        """NFR-SEC-005: through a proxy the guard would only see the proxy, so proxies are off."""
        with patch.dict(os.environ, {'HTTPS_PROXY': 'http://127.0.0.1:3128', 'https_proxy': 'http://127.0.0.1:3128'}):
            egress.disable_proxies()
            self.assertEqual(requests.utils.get_environ_proxies('https://services.odoo.com/'), {})
            with network_fence() as fence, self.assertRaises(requests.exceptions.ConnectionError):
                requests.get('https://services.odoo.com/', timeout=5)
        self.assertEqual([attempt[0] for attempt in fence.blocked], ['services.odoo.com'])
        self.assertEqual(fence.reached, [])


@tagged('post_install', '-at_install', 'hisabkar_privacy')
class TestVendorFeaturesNeutralised(RealRequestsMixin, TransactionCase):
    """NFR-SEC-005/006: every known data flow from the ADR-0005 audit is off."""

    def test_usage_report_collects_and_sends_nothing(self):
        contract = self.env['publisher_warranty.contract']
        with network_fence() as fence:
            self.assertEqual(contract._get_message(), {})
            self.assertFalse(contract.update_notification(cron_mode=False))
            self.assertFalse(contract.update_notification(cron_mode=True))
            with self.assertRaises(egress.EgressBlocked):
                contract._get_sys_logs()
            # Through upstream's own caller too: the scheduled job.
            self.env.ref('mail.ir_cron_module_update_notification').method_direct_trigger()
        self.assertFalse(fence.blocked)
        self.assertEqual(fence.reached, [])
        self.assertFalse(self.env.ref('mail.ir_cron_module_update_notification').active)

    def test_paid_service_modules_removed(self):
        installed = self.env['ir.module.module'].search([('state', '=', 'installed')])
        self.assertFalse(installed.filtered(lambda m: is_blocked_name(m.name)).mapped('name'))

    def test_paid_service_module_install_refused(self):
        sms = self.env['ir.module.module'].search([('name', '=', 'sms')])
        self.assertTrue(sms)
        with self.assertRaises(UserError):
            sms.button_install()

    def test_blocked_modules_are_never_auto_install_candidates(self):
        modules = self.env['ir.module.module'].search([])
        self.assertFalse(modules.filtered('auto_install')._hisabkar_blocked().mapped('name'))
        self.env['ir.module.module'].update_list()
        self.assertFalse(modules.filtered('auto_install')._hisabkar_blocked().mapped('name'))

    def test_install_with_blocked_auto_install_dependants_terminates(self):
        """Regression: installing a module whose auto-install companions are blocked (Italian
        accounting pulls in an IAP-based e-invoicing module) used to loop forever."""
        Module = self.env['ir.module.module']
        l10n_it = Module.search([('name', '=', 'l10n_it')])
        self.assertTrue(l10n_it)
        l10n_it.button_install()
        to_install = Module.search([('state', '=', 'to install')])
        self.assertIn(l10n_it, to_install)
        self.assertFalse(to_install._hisabkar_blocked().mapped('name'))

    def test_vendor_endpoints_point_nowhere(self):
        params = self.env['ir.config_parameter'].sudo()
        for key in ENDPOINT_PARAMS:
            with self.subTest(key=key):
                self.assertEqual(params.get_param(key), DEAD_ENDPOINT)

    def test_gravatar_off_through_email_onchange(self):
        """Upstream's caller: typing an email on a contact looks up its Gravatar."""
        with network_fence() as fence:
            partner = self.env['res.partner'].with_context(gravatar_image=True).new({'name': 'Privacy Test'})
            partner.email = 'someone@example.org'
            partner.onchange_email()
        self.assertFalse(partner.image_1920)
        self.assertFalse(fence.blocked)
        self.assertEqual(fence.reached, [])

    def test_link_previews_off_everywhere(self):
        partner = self.env['res.partner'].create({'name': 'Privacy Test', 'email': 'someone@example.org'})
        message = partner.message_post(body='<p><a href="https://example.org/page">link</a></p>')
        LinkPreview = self.env['mail.link.preview']
        with network_fence() as fence:
            self.assertFalse(LinkPreview._is_link_preview_enabled())
            LinkPreview._create_from_message_and_notify(message)
            self.assertFalse(LinkPreview._search_or_create_from_url('https://example.org/page'))
        self.assertFalse(message.link_preview_ids)
        self.assertFalse(fence.blocked)
        self.assertEqual(fence.reached, [])

    def test_overridden_upstream_methods_still_exist(self):
        """If upstream renames a method we override, our override silently stops applying.

        Fail loudly instead (docs/upstream-patches.md row 2).
        """
        overrides = {
            'ir.model.data': ['_process_end'],
            'ir.module.module': ['_state_update', 'button_install', 'update_list'],
            'publisher_warranty.contract': ['_get_message', '_get_sys_logs', 'update_notification'],
            'mail.link.preview': ['_is_link_preview_enabled', '_create_from_message_and_notify',
                                  '_search_or_create_from_url'],
            'res.partner': ['_get_gravatar_image'],
            'ir.http': ['_post_dispatch', '_handle_error'],
        }
        ours = egress.__name__.rsplit('.', 1)[0]
        for model, methods in overrides.items():
            upstream_classes = [cls for cls in type(self.env[model]).__mro__
                                if not cls.__module__.startswith(ours)]
            for method in methods:
                with self.subTest(model=model, method=method):
                    self.assertTrue(any(method in vars(cls) for cls in upstream_classes))


@tagged('post_install', '-at_install', 'hisabkar_privacy')
class TestScheduledJobsStayLocal(RealRequestsMixin, TransactionCase):
    """NFR-SEC-005 acceptance criterion: every scheduled job runs without reaching outward."""

    def test_every_cron_runs_without_outbound_attempt(self):
        # Jobs that commit fail inside a test transaction and log their own tracebacks; mute every
        # framework logger by name (a filter on a parent logger does not apply to its children).
        # The assertion relies on the guard's record and the fence, not on logs.
        root = ir_cron._logger.name.split('.')[0]
        loggers = [name for name in logging.root.manager.loggerDict if name.split('.')[0] == root]
        not_run = []
        # The test framework also dumps a stack to stderr on every forbidden commit; silence it here.
        with network_fence() as fence, mute_logger(*loggers), patch('traceback.print_stack'):
            for cron in self.env['ir.cron'].with_context(active_test=False).search([]):
                try:
                    with self.env.cr.savepoint():
                        cron.method_direct_trigger()
                except Exception as e:  # noqa: BLE001 - a job that cannot run in a test still must not call out
                    not_run.append(f'{cron.name}: {type(e).__name__}')
        self.assertEqual(list(fence.blocked), [], f"jobs tried to reach outward; jobs that could not run in a test: {not_run}")
        self.assertEqual(fence.reached, [])
