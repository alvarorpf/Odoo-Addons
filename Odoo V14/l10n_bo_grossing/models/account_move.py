from odoo import fields, models, api
from odoo.exceptions import UserError


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    def action_inverse_tax(self):
        context = {}
        context['active_ids'] = self.ids
        context['invoice_line_id'] = len(self.ids) > 0 and self.ids[0] or False
        view_id = self.env.ref('l10n_bo_grossing.tax_inverse_wizard_form').id
        wizard_form = {
            'name': u"Cálculo precio inverso",
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'tax.inverse.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': str([]),
            'target': 'new',
            'context': context,
        }
        return wizard_form