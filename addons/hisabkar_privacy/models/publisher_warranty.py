from odoo import api, models

from ..egress import EgressBlocked


class PublisherWarrantyContract(models.AbstractModel):
    """The vendor's weekly usage report (NFR-SEC-005).

    Upstream collects the database UUID, URL, user counts, installed apps and the company's name,
    email and phone, and posts them to the vendor. Every entry point is neutralised here, so nothing
    is collected and nothing is sent, whoever calls it (the cron, or a module's install hook).
    """
    _inherit = 'publisher_warranty.contract'

    @api.model
    def _get_message(self):
        return {}

    @api.model
    def _get_sys_logs(self):
        raise EgressBlocked("The usage report is disabled by Hisabkar's privacy policy (ADR-0005)")

    def update_notification(self, cron_mode=True):
        return False
