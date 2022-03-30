# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class BankingTransactionMod(models.Model):
    _name = 'banking.transaction.mod'
    _description = 'Transaccion'

    name = fields.Char('Nombre', required=True)
    code = fields.Integer('Codigo', required=True)
