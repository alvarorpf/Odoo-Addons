# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OpScholarshipDiscount(models.TransientModel):
    _name = 'op.scholarship.discount'

    scholarship_id = fields.Many2one('op.scholarship', 'Beca y Descuento')
    type_discount = fields.Selection([('porcentaje', 'Porcentaje'), ('monto', 'Monto Total')], 'Tipo de Descuento',
                                     required=True)
    amount = fields.Char('Monto', required=True)

    @api.multi
    def apply_discount(self):
        if self.scholarship_id:
            if self.type_discount == 'porcentaje':
                self.scholarship_id.discount = self.amount
                self.scholarship_id.discount_total = 0
            else:
                self.scholarship_id.discount_total = self.amount
                self.scholarship_id.discount = 0
