# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OpReportSedes(models.TransientModel):
    _name = "op.report.sedes.wizard"

    start_date = fields.Date('Fecha Desde')
    end_date = fields.Date('Fecha Hasta')

    @api.multi
    def generate_report(self):
        data = self.read()[0]
        return self.env.ref('poi_op_health.op_report_sedes').report_action(self, data=data)
