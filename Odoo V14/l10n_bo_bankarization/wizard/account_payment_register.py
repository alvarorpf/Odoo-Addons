# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    is_banking = fields.Boolean("Bancarizacion", compute="_compute_banking")
    banking = fields.Boolean("Bancarizacion ", default=False)
    transaction_mod_id = fields.Many2one("banking.transaction.mod", "Modalidad de Transaccion")
    transaction_type_id = fields.Many2one("banking.transaction.type", "Tipo de Transaccion")
    contract_number = fields.Char("Numero de Contrato")
    account_number = fields.Char("Nro. Cuenta Documento de Pago")
    nit_origin = fields.Char("NIT Entidad Financiera Emisora")
    document_number = fields.Char("Nro. Documento de Pago")
    document_type_id = fields.Many2one("banking.document.type", "Tipo Documento de Pago")
    document_date = fields.Date("Fecha de Documento de Pago")

    @api.depends('amount')
    def _compute_banking(self):
        for r in self:
            if r.amount >= 50000:
                r.update({
                    'is_banking': True,
                    'banking': True,
                })
            else:
                r.update({
                    'is_banking': False,
                    'banking': False,
                })

    def _create_payment_vals_from_wizard(self):
        payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        if self.is_banking:
            payment_vals['banking'] = self.banking
            payment_vals['transaction_mod_id'] = self.transaction_mod_id and self.transaction_mod_id.id or False
            payment_vals['transaction_type_id'] = self.transaction_type_id and self.transaction_type_id.id or False
            payment_vals['contract_number'] = self.contract_number
            payment_vals['account_number'] = self.account_number
            payment_vals['nit_origin'] = self.nit_origin
            payment_vals['document_number'] = self.document_number
            payment_vals['document_type_id'] = self.document_type_id and self.document_type_id.id or False
            payment_vals['document_date'] = self.document_date
        return payment_vals
