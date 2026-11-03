from odoo import api, models


class MailLinkPreview(models.Model):
    """NFR-SEC-006: upstream fetches every URL pasted into chatter from the server, which tells
    third-party sites what our users are discussing. Every entry point is closed: the client is
    told previews are off, and the server-side builders produce nothing."""
    _inherit = 'mail.link.preview'

    @api.model
    def _is_link_preview_enabled(self):
        return False

    @api.model
    def _create_from_message_and_notify(self, message, request_url=None):
        return self

    @api.model
    def _search_or_create_from_url(self, url):
        return self.browse()
