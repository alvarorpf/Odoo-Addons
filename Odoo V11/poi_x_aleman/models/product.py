# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime


class ProductTemplate(models.Model):
    _inherit = "product.template"

    charge_type = fields.Selection(
        string='Tipo de Cargo',
        selection=[
            ('charge', 'Cargo'),
            ('payment', 'Abono')
        ]
    )
    concept_type = fields.Selection(
        string='Concepto',
        selection=[
            ('material', 'Material'),
            ('due', 'Mora'),
            ('pension', 'Pension')
        ]
    )
    
