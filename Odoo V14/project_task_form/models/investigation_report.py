# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import datetime

class InvestigationReport(models.Model):
    _name = "investigation.report"

    state = fields.Selection([('draft', 'Borrador'), ('finished', 'Completado')], string="Estado", default='draft')
    task_id = fields.Many2one('project.task', 'Tarea')
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company.id)
    date = fields.Date('Fecha', default=datetime.date.today())
    name = fields.Char("Nombre", default="Nuevo")
    social_reason = fields.Char("Razon Social")
    rut = fields.Char("RUT")
    project_id = fields.Many2one('project.project', "Centro de Costo")
    direction = fields.Text("Ubicacion /  Direccion del centro de costo")
    boss = fields.Char("Supervisor / Jefe CC")
    kam = fields.Char("KAM (Gerente Cuenta)")

    injured = fields.Char("Nombre Lesionado (a)")
    rut_injured = fields.Char("RUT")
    position = fields.Char("Cargo en el CC")
    age = fields.Integer("Edad")
    antiquity = fields.Integer("Antigüedad en el cargo")
    antiquity_company = fields.Integer("Antigüedad en la empresa")
    direct_boss = fields.Char("Nombre Jefe Directo")
    contract_type = fields.Selection([('term', 'Plazo Fijo'), ('undefined', 'Indefinido'), ('chore', 'Obra o Faena')], "Tipo de Contrato")

    datetime_accident = fields.Datetime("Fecha/Hora de Accidente", required=True, default=datetime.datetime.now())
    accident_day = fields.Selection([
        ('L', 'Lunes'),
        ('MA', 'Martes'),
        ('MI', 'Miercoles'),
        ('J', 'Jueves'),
        ('V', 'Viernes'),
        ('S', 'Sabado'),
        ('D', 'Domingo'),
    ], string="Dia del Accidente")
    crash_site = fields.Text("Lugar del accidente")
    accident_cause = fields.Char("Agente del Accidente")
    accident_source = fields.Char("Fuente del Accidente")
    activity = fields.Char("La actividad esta en el contrato")
    training = fields.Char("El lesionado recibio capacitacion?")
    matriz = fields.Char("La actividad y peligro esta evaluada en la matriz IPER")
    procedure = fields.Char("Existe procedimiento o art. de la actividad")
    accident_type = fields.Char("Tipo de Accidente o Contacto (golpeado por, contra, otro)")
    affected_part = fields.Char("Parte del cuerpo afectada")
    injury_type = fields.Char("Tipo de Lesion")

    description = fields.Text("Descripcion del accidente")

    evidence_ids = fields.One2many("investigation.report.evidence", "investigation_id", "Evidencias")
    measure_ids = fields.One2many("investigation.report.measure", "investigation_id", "Medidas de Control")

    signature = fields.Binary('Firma', copy=False)

    @api.model
    def create(self, vals):
        res = super(InvestigationReport, self).create(vals)
        if res.name == 'Nuevo':
            sequence = self.env['ir.sequence'].search([('code', '=', 'sequence.investigation.report')])
            res.name = sequence.next_by_id() or _('Nuevo')
        return res

    def action_confirm(self):
        for r in self:
            if not r.signature:
                raise UserError(_("Debe registrar la firma correspondiente del documento."))
            r.state = 'finished'
            if r.task_id:
                content, content_type = self.env.ref('project_task_form.action_report_investigation_report')._render(r.id)
                self.env['ir.attachment'].create({
                    'name': r.task_id.name and _(r.name + " - %s.pdf", r.task_id.name) or _("Reporte Investigacion de Accidentes.pdf"),
                    'type': 'binary',
                    'datas': base64.encodebytes(content),
                    'res_model': r.task_id._name,
                    'res_id': r.task_id.id
                })


class InvestigationReportEvidence(models.Model):
    _name = "investigation.report.evidence"

    investigation_id = fields.Many2one("investigation.report", "Investigacion")
    file = fields.Char("Nombre Testigo")


class InvestigationReportMeasure(models.Model):
    _name = "investigation.report.measure"

    investigation_id = fields.Many2one("investigation.report", "Investigacion")
    action = fields.Char("Accion Correctiva / Preventiva")
    date = fields.Date("Fecha Implementacion", required=True, default=datetime.date.today())
    responsible = fields.Text("Responsables")
    correct_action = fields.Boolean("Cumple Implementacion")
    reprogramming_action = fields.Boolean("Reprogramar Implementacion")

