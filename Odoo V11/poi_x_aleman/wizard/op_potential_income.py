# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OpPotentialIncome(models.TransientModel):
    _name = "op.potential.income.wizard"

    date = fields.Date('Fecha')

    @api.multi
    def generate_report(self):
        data = self.read()[0]
        return self.env.ref('poi_x_aleman.potential_income_report').report_action(self, data=data)