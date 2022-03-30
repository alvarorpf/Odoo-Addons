# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class AccountPayment(models.Model):
    _inherit = 'account.payment'

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
