# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    charge_request_id = fields.Many2one('op.request.charge', 'Cargo a Pagar')

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        base_document = False
        if self.env.context.get("default_charge_request_id"):
            base_document = self.env['op.request.charge'].browse(self.env.context.get("default_charge_request_id"))
            # rec['currency_id'] = base_document.currency_id.id
            rec['amount'] = base_document.amount_total or 0.0
            rec['charge_request_id'] = base_document.id
        # Map accordingly
        if base_document:
            # if base_document.account_analytic_id:
            #     rec['analytic_account_id'] = base_document.account_analytic_id.id
            rec['payment_type'] = 'inbound'
            rec['partner_type'] = 'customer'
            rec['partner_id'] = base_document.partner_id and base_document.partner_id.id
        return rec

    @api.multi
    def post(self):
        for payment in self:
            super(AccountPayment, self).post()
            request2 = payment.charge_request_id or False
            if request2:
                request2.payment_id = payment.id
                request2.action_done_charge()
