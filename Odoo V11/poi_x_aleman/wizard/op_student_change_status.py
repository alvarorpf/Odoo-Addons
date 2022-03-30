# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OpStudentChangeStatus(models.TransientModel):
    _name = "op.student.change.status"

    student_id = fields.Many2one('op.student', 'Estudiante')
    state = fields.Selection([('activo', 'Activo'), ('inactivo', 'Inactivo')], 'Cambiar a', required=True)
    case_id = fields.Many2one('op.student.case', 'Caso')
    reason = fields.Char('Razon')
    date_change = fields.Date('Fecha de Cambio', default=fields.Datetime.now)

    @api.onchange('state')
    def get_case(self):
        case_obj = self.env['op.student.case']
        if self.state == 'activo':
            state = True
        else:
            state = False
        case_ids = case_obj.search([('apply_active', '=', state)])
        return {
            'domain': {
                'case_id':
                    [
                        ('id', 'in', case_ids.ids)
                    ]
            }
        }

    @api.multi
    def change_student_status(self):
        self.student_id.state = self.state
        self.student_id.case_id = self.case_id.id
