# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def action_view_clinical_record(self):
        return {
            'name': 'Registro Clinicos',
            'domain': [('employee_id', '=', self.id)],
            'res_model': 'op.clinical.record',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }
