# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpStudent(models.Model):
    _inherit = 'op.student'

    def action_view_medical_file(self):
        return {
            'name': 'Ficha Medica',
            'domain': [('student_id', '=', self.id)],
            'res_model': 'op.medical.file',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }

    def action_view_clinical_record(self):
        return {
            'name': 'Registro Clinico',
            'domain': [('student_id', '=', self.id)],
            'res_model': 'op.clinical.record',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }

    def action_view_exit_authorization(self):
        return {
            'name': 'Autorizacion de Salida',
            'domain': [('student_id', '=', self.id)],
            'res_model': 'op.exit.authorization',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }
