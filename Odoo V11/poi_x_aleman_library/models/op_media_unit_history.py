from odoo import models, fields, api


class OpmediaUnitHistory(models.Model):
    _name = 'op.media.unit.history'
    _description = 'Historial de Prestamo'

    @api.multi
    @api.depends('type', 'student_id', 'teacher_id', 'employee_id')
    def _compute_name(self):
        for r in self:
            if r.type == 'student':
                r.name = r.student_id.full_name
                r.teacher_id = ''
                r.employee_id = ''
            if r.type == 'teacher':
                r.name = r.teacher_id.full_name
                r.student_id = ''
                r.employee_id = ''
            if r.type == 'employee':
                r.name = r.employee_id.name
                r.student_id = ''
                r.teacher_id = ''

    name = fields.Char('Nombre', store=True, compute='_compute_name')
    type = fields.Selection([('student', 'Alumno'), ('teacher', 'Profesor'), ('employee', 'Empleado')], string="Tipo")
    media_unit_id = fields.Many2one('op.media.unit', 'Unidad')
    media_state_id = fields.Many2one('op.book.state', 'Estado de la Unidad')
    student_id = fields.Many2one('op.student', 'Alumno')
    teacher_id = fields.Many2one('op.faculty', 'Profesor')
    employee_id = fields.Many2one('res.users', 'Empleado')
    out_date = fields.Date('Fecha de Salida')
    return_date = fields.Date('Fecha de Retorno')
    observations = fields.Char('Observaciones')

