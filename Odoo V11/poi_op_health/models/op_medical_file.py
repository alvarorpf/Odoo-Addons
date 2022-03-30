# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class OpMedicalFile(models.Model):
    _name = 'op.medical.file'
    _description = 'Ficha Medica'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', default='Nuevo', readonly=True)
    # Datos Personales
    student_id = fields.Many2one('op.student', 'Alumno', required=True)
    student_family_code = fields.Many2one('op.family', 'Codigo de Familia', compute='_compute_family_code')

    # Contactos de emergencia
    clinical_contact_id = fields.One2many('op.medical.file.emergency.contact', 'medical_file_id',
                                          'Contactos de Emergencia')
    # emergecy_contact

    # Cobertura Medica
    private_insurance = fields.Selection([('si', 'SI'), ('no', 'NO')], 'Seguro Particular')
    insurance_name = fields.Char('Nombre del Seguro')
    insurance_phone = fields.Integer('Telefono del Seguro')
    medical_center = fields.Char('Centro Medico de Referencia')
    phone_medical_center = fields.Integer('Telefono Centro')
    family_doctor = fields.Char('Medico pediatra o de cabecera')
    phone_doctor = fields.Integer('Telefono')
    clinical_disease_id = fields.One2many('op.medical.file.diseases', 'medical_file_id', 'Enfermedades')

    # Antecedentes de Interes
    operations = fields.Char('Operaciones')
    fractures = fields.Char('Traumatismos/Fracturas')
    coagulation_problems = fields.Char('Problemas de Coagulacion')
    blood_group_id = fields.Many2one('op.blood.group', 'Grupo Sanguineo')

    # vacunas
    clinical_vaccine_id = fields.One2many('op.medical.file.vaccines', 'medical_file_id', 'Vacunas')

    # alergias
    clinical_allergy_id = fields.One2many('op.medical.file.allergy', 'medical_file_id', 'Alergias')

    # medicacion
    clinical_frequency_id = fields.One2many('op.medical.file.medicines', 'medical_file_id', 'Frecuencia de Medicinas')
    contraindicated_medications = fields.Text('Medicamentos Contraindicados', required=True)

    # Deportes que no debe practicar
    sport_ids = fields.Many2many('op.sport', string='Deportes')

    @api.multi
    @api.depends('student_id')
    def _compute_family_code(self):
        for record in self:
            if record.student_id:
                record.student_family_code = (
                                                         record.student_id.family_code and record.student_id.family_code.id) or False

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sequence.medical.file') or '/'
        return super(OpMedicalFile, self).create(vals)


class OpMedicalFileEC(models.Model):
    _name = 'op.medical.file.emergency.contact'

    medical_file_id = fields.Many2one('op.medical.file')
    relationship_id = fields.Many2one('op.relationship', 'Relacion')
    name = fields.Char('Nombre')
    phones = fields.Char('Telefonos')


class OpMedicalFileD(models.Model):
    _name = 'op.medical.file.diseases'

    medical_file_id = fields.Many2one('op.medical.file')
    disease_id = fields.Many2one('op.diseases.list', 'Enfermedades')
    age = fields.Char('Edad en que Padecio')


class OpMedicalFileV(models.Model):
    _name = 'op.medical.file.vaccines'

    medical_file_id = fields.Many2one('op.medical.file')
    vaccine_id = fields.Many2one('op.vaccines.list', 'Vacunas')
    has = fields.Boolean('Tiene')


class OpMedicalFileFA(models.Model):
    _name = 'op.medical.file.allergy'

    medical_file_id = fields.Many2one('op.medical.file')
    allergy_id = fields.Many2one('op.allergy.list', 'Alergias')
    reaction = fields.Char('Reaccion')
    medication = fields.Char('Medicacion Utilizada')


class OpMedicalFileFM(models.Model):
    _name = 'op.medical.file.medicines'

    medical_file_id = fields.Many2one('op.medical.file')
    name = fields.Char('Nombre de Medicamento')
    dose = fields.Char('Dosis')
    frequency_id = fields.Many2one('op.medicines.frequency', 'Frecuencia')
    side_effects = fields.Char('Efectos Secundarios')
    use_reasons = fields.Char('Motivo de Uso')


class MedicalFileReport(models.AbstractModel):
    _name = 'report.poi_op_health.op_medical_file_report'

    @api.multi
    def get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('poi_op_health.op_medical_file_report')
        docs = self.env[report.model].search([('id', '=', docids[0])])
        year = datetime.datetime.now().year
        period = self.env['op.school.period'].search([('year_id', '=', str(year))])

        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'data': data,
            'period': period,
        }
