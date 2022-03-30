# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class OpFaculty(models.Model):
    _inherit = 'op.faculty'

    blood_group_id = fields.Many2one('op.blood.group', 'Grupo Sanguineo')

    def action_view_clinical_record(self):
        return {
            'name': 'Registro Clinicos',
            'domain': [('teacher_id', '=', self.id), ('student_id', '=', False)],
            'res_model': 'op.clinical.record',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }
