# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReSupplierList(models.Model):
    _name = 're.supplier.list'
    _inherit = 'res.partner'

    last2 = fields.Char("A. Materno")
