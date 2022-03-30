# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class PosEstablishment(models.Model):
    _name = 'pos.establishment'

    name = fields.Char("Nombre", required=True)
    conciliation_account_id = fields.Many2one("account.account", "Cuenta de Conciliación", required=True)
    commission_account_id = fields.Many2one("account.account", "Cuenta de Comisión", required=True)
    percentage = fields.Float("Porcentaje(%)", required=True)
    journal_id = fields.Many2one("account.journal", "Diario Contable", required=True)
    pos_payment_method_id = fields.Many2one("pos.payment.method", "Método de Pago POS", required=True)

