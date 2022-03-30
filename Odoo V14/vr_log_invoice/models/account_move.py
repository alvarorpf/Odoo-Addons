import datetime

from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    log_ids = fields.One2many('account.move.log', 'invoice_id', 'Log de Facturas')

    def action_print_original(self):
        for r in self:
            log_obj = self.env['account.move.log']
            log_obj.create({
                'invoice_id': r.id or False,
                'user_id': self.env.user and self.env.user.id or False,
                'date': datetime.date.today(),
                })
        res = super(AccountMove, self).action_print_original()
        return res

    # def action_print_copy(self):
    #     self.ensure_one()
    #     report_name = 'l10n_bo_invoice.report_invoice_bol_copia'
    #     return self.env['ir.actions.report'].search(
    #         [
    #             ('report_name', '=', report_name),
    #             ('report_type', '=', 'qweb-pdf')
    #         ], limit=1
    #     ).report_action(self)

