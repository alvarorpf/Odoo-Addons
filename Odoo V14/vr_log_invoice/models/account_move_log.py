# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class AccountMoveLog(models.Model):
    _name = 'account.move.log'
    _description = 'Log de impresion de facturas'

    invoice_id = fields.Many2one('account.move', string='Factura', required=True)
    user_id = fields.Many2one('res.users', 'Usuario')
    date = fields.Date('Fecha de impresion')