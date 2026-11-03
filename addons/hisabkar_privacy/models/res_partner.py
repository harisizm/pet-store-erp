from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_gravatar_image(self, email):
        # NFR-SEC-006: upstream sends a hash of the customer's email to gravatar.com.
        return False
