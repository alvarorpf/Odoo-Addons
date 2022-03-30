# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class OpClinicalRecordP(models.Model):
    _name = 'op.clinical.report.parameters'

    record_id = fields.Many2one('op.clinical.record', 'Historia Clinica')
    parameter_id = fields.Many2one('op.report.parameters', 'Parametro')
    value_id = fields.Many2one('op.value.report.parameters', 'Valor')

    @api.onchange('parameter_id')
    def get_values(self):
        for record in self:
            if record.parameter_id:
                return {
                    'domain': {
                        'value_id':
                            [
                                ('parameter_id', '=', (record.parameter_id and record.parameter_id.id) or False)
                            ]
                    }
                }


class OpClinicalRecord(models.Model):
    _name = 'op.clinical.record'
    _description = 'Registro Clínico'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.multi
    @api.depends('student_id')
    def _compute_student(self):
        for record in self:
            if record.student_id:
                record.family_code_id = (record.student_id.family_code and record.student_id.family_code.id) or False
                record.course_id = (record.student_id.course_id and record.student_id.course_id.id) or False
                record.age = record.student_id.age

    @api.multi
    @api.depends('type', 'student_id', 'teacher_id', 'employee_id')
    def _compute_patient(self):
        for r in self:
            if r.type == 'student':
                r.patient_name = r.student_id.name
                r.code = r.student_id.student_code
            if r.type == 'teacher':
                r.patient_name = r.teacher_id.full_name
                r.code = r.teacher_id.initials
            if r.type == 'employee':
                r.patient_name = r.employee_id.name

    name = fields.Char('Nombre', default='Nuevo', readonly=True)
    patient_name = fields.Char('Paciente', compute='_compute_patient')
    code = fields.Char('Codigo/Sigla', compute="_compute_patient")
    type = fields.Selection([('student', 'Alumno'), ('teacher', 'Profesor'), ('employee', 'Empleado')], string="Tipo")
    # Datos de Alumno
    student_id = fields.Many2one('op.student', 'Alumno')
    family_code_id = fields.Many2one('op.family', 'Codigo de Familia', compute='_compute_student')
    age = fields.Integer('Edad', compute='_compute_student')

    # Datos Academicos
    course_id = fields.Many2one('op.batch', 'Curso', compute='_compute_student')
    teacher_id = fields.Many2one('op.faculty', 'Profesor')
    employee_id = fields.Many2one('hr.employee', 'Administrativo')

    # Registro Clinico
    consultation_reason_id = fields.Many2one('op.consultation.reason', 'Razon de Consulta', required=True)
    measure_taken_id = fields.Many2one('op.measure.taken', 'Medida Tomada', required=True)
    datetime_arrival = fields.Datetime('Fecha y Hora de Llegada', required=True, default=fields.Datetime.now)
    datetime_departure = fields.Datetime('Fecha y Hora de Salida', required=True)

    # Parametros Reporte
    clinical_parameters_ids = fields.One2many('op.clinical.report.parameters', 'record_id', 'Parametros de Reporte')

    # Observaciones
    observations = fields.Text('Observaciones')

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sequence.clinical.record') or '/'
        return super(OpClinicalRecord, self).create(vals)
