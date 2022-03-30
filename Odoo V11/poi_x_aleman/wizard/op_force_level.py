# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class OpStudentForceLevel(models.TransientModel):
    _name = "op.student.force.level"

    student_id = fields.Many2one('op.student', 'Estudiante')
    level = fields.Many2one('account.op.charge.level', 'Nivel')

    @api.multi
    def force_level(self):
        for record in self:
            if not int(record.level.name) > len(record.student_id.family_code.childs_ids):
                record.student_id.forced_level_id = record.level.id
                record.student_id.pension_calculation()
            else:
                record.student_id.forced_level_id = ''
                raise UserError(_('No puede forzar un nivel mayor a %s.') % (
                    len(record.student_id.family_code.childs_ids)))

