from odoo import api, models


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    @api.model
    def _process_end(self, modules):
        # NFR-SEC-005: purge here, not in this module's own data file. The loader calls this once
        # every module of the install/update pass is loaded and just before it uninstalls modules
        # marked 'to remove', so blocked modules installed in the same pass (a fresh database
        # installs the whole IAP family alongside us) are all present and all removed in this run.
        # Purging earlier marked some of them while their dependants were still queued, which left
        # a database with `iap` removed but `sms` installed.
        res = super()._process_end(modules)
        self.env['ir.module.module']._hisabkar_purge_blocked()
        return res
