from odoo import api, models

# Where upstream code looks up the vendor's endpoints. Pointed at a closed local port so that even a
# path the egress guard somehow missed fails locally (ADR-0005, layer 3).
DEAD_ENDPOINT = 'http://127.0.0.1:9'
ENDPOINT_PARAMS = ('iap.endpoint', 'web_editor.media_library_endpoint', 'snailmail.endpoint')


class HisabkarPrivacy(models.AbstractModel):
    _name = 'hisabkar.privacy'
    _description = 'Hisabkar privacy hardening'

    @api.model
    def _harden(self):
        """NFR-SEC-005/006: run on every install and upgrade (data/hisabkar_privacy_data.xml).

        Module removal is not done here but at the end of the loading pass (ir_model_data.py).
        """
        cron = self.env.ref('mail.ir_cron_module_update_notification', raise_if_not_found=False)
        if cron and cron.active:
            cron.active = False
        params = self.env['ir.config_parameter'].sudo()
        for key in ENDPOINT_PARAMS:
            params.set_param(key, DEAD_ENDPOINT)
        # Tells the web client link previews are off (mail_link_preview.py closes the server side).
        params.set_param('mail.link_preview_throttle', 0)
        self.env['ir.module.module']._hisabkar_disable_auto_install()
