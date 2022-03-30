# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class BankingDocumentType(models.Model):
    _name = 'banking.document.type'
    _description = 'Tipo de documento'

    name = fields.Char('Nombre', required=True)
    code = fields.Integer('Codigo', required=True)
