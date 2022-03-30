# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class OpExitAuthorization(models.Model):
    _name = 'op.exit.authorization'

    name = fields.Char('Nombre', default='Nuevo', readonly=True)
    authorization_type = fields.Selection([('medica', 'Medica'), ('ausencia', 'Ausencia')], 'Tipo de Autorizacion', required=True)
    # Datos de Alumno
    student_id = fields.Many2one('op.student', 'Alumno', required=True)
    family_code_id = fields.Many2one('op.family', 'Codigo de Familia', compute='_compute_student')

    # Datos Academicos
    course_id = fields.Many2one('op.batch', 'Curso', compute='_compute_student')
    teacher_id = fields.Many2one('op.faculty', 'Profesor', required=True)

    # Registro Clinico
    consultation_reason_id = fields.Many2one('op.consultation.reason', 'Razon de Consulta')
    datetime_authorization = fields.Datetime('Fecha y Hora de Autorizacion', default=fields.Datetime.now)
    datetime_departure = fields.Datetime('Fecha y Hora de Salida')

    #Motivos de Ausencia
    absence_reason = fields.Char('Motivo de Ausencia')
    datetime_absence = fields.Datetime('Fecha y Hora de Ausencia')

    #Datos de Gondola
    bus_number = fields.Char('Nro de gondola')
    bus_route = fields.Char('Ruta de gondola')

    #Observaciones
    observations = fields.Text('Observaciones')

    #Usuario
    logged_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.uid)

    @api.multi
    @api.depends('student_id')
    def _compute_student(self):
        for record in self:
            if record.student_id:
                record.family_code_id = (record.student_id.family_code and record.student_id.family_code.id) or False
                record.course_id = (record.student_id.course_id and record.student_id.course_id.id) or False

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sequence.exit.authorization') or '/'
        return super(OpExitAuthorization, self).create(vals)
