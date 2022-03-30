# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    charge_request_id = fields.Many2one('op.request.charge', 'Cargo a Pagar')
    asset_sequence = fields.Integer('Secuenciador de Activos', default=1)