# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class BankingTransactionType(models.Model):
    _name = 'banking.transaction.type'
    _description = 'Tipo de transaccion'

    name = fields.Char('Nombre', required=True)
    code = fields.Integer('Codigo', required=True)
