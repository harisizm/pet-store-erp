import re

from odoo import _, api, models
from odoo.exceptions import UserError

# NFR-SEC-005. Modules that send data to the vendor's paid services or proxies, from the ADR-0005
# audit (2026-11-03). Anything depending on one of them, at any depth, is blocked too.
BLOCKED_MODULES = frozenset({
    'iap', 'iap_mail', 'iap_crm', 'sms', 'snailmail', 'snailmail_account',
    'partner_autocomplete', 'web_unsplash', 'account_edi_proxy_client', 'account_peppol',
})
BLOCKED_PATTERN = re.compile(r'(^|_)iap($|_)|_sms$|^snailmail')


def is_blocked_name(name):
    return name in BLOCKED_MODULES or bool(BLOCKED_PATTERN.search(name))


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def _hisabkar_blocked(self):
        """Modules in self that are blocked by name or depend, at any depth, on a blocked module."""
        blocked = self.browse()
        for module in self:
            todo, seen = module, self.browse()
            while todo:
                if any(is_blocked_name(name) for name in todo.mapped('name')):
                    blocked |= module
                    break
                seen |= todo
                todo = todo.dependencies_id.depend_id - seen
        return blocked

    @api.model
    def _hisabkar_disable_auto_install(self):
        """Take blocked modules out of upstream's auto-install selection (NFR-SEC-005).

        Upstream's button_install loops until no auto-install candidate is left. Dropping a blocked
        candidate later (in _state_update) would leave it qualifying forever, so it must never be a
        candidate. Re-applied after every update_list, which rewrites auto_install from manifests.
        """
        blocked = self.search([('auto_install', '=', True)])._hisabkar_blocked()
        if blocked:
            blocked.write({'auto_install': False})

    @api.model
    def update_list(self):
        res = super().update_list()
        self._hisabkar_disable_auto_install()
        return res

    def button_install(self):
        # NFR-SEC-005: an explicit request for a blocked module is refused, not silently ignored.
        if blocked := self._hisabkar_blocked():
            raise UserError(_(
                "Hisabkar's privacy policy blocks these modules because they send data to outside "
                "services or depend on modules that do: %(modules)s",
                modules=', '.join(blocked.mapped('name')),
            ))
        return super().button_install()

    def _state_update(self, newstate, states_to_update, level=100):
        # Backstop for dependencies pulled in through _state_update's own recursion; auto-install
        # candidates are already excluded by _hisabkar_disable_auto_install.
        if newstate == 'to install':
            self -= self._hisabkar_blocked()  # noqa: PLW0642
        return super()._state_update(newstate, states_to_update, level=level)

    @api.model
    def _hisabkar_purge_blocked(self):
        """Mark every installed blocked module for removal (NFR-SEC-005).

        Refuses, rather than cascades, if removing them would also remove a module that is not
        itself blocked: that would silently uninstall something a shop relies on.
        """
        self._hisabkar_disable_auto_install()
        installed = self.search([('state', 'in', ('installed', 'to upgrade'))])
        to_remove = installed.filtered(lambda m: is_blocked_name(m.name))
        if not to_remove:
            return
        collateral = to_remove.downstream_dependencies(exclude_states=('uninstalled', 'uninstallable', 'to remove'))
        collateral = collateral.filtered(lambda m: not is_blocked_name(m.name))
        if collateral:
            raise UserError(_(
                "Removing the blocked modules would also remove %(modules)s. Resolve this by hand "
                "before installing Hisabkar Privacy.",
                modules=', '.join(collateral.mapped('name')),
            ))
        to_remove.button_uninstall()
