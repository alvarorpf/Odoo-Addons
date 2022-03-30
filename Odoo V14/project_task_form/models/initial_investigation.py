# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import datetime


class InitialInvestigation(models.Model):
    _name = "initial.investigation"

    state = fields.Selection([('draft', 'Borrador'), ('finished', 'Completado')], string="Estado", default='draft')
    task_id = fields.Many2one('project.task', 'Tarea')
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company.id)
    date = fields.Date('Fecha', default=datetime.date.today())
    name = fields.Char("Nombre", default="Nuevo")
    injured = fields.Char("Nombre Accidentado")
    rut = fields.Char("RUT")
    age = fields.Integer("Edad")
    position = fields.Char("Cargo")
    project_id = fields.Many2one('project.project', "Centro de costo del Accidentado")
    date_entry = fields.Date("Fecha de Ingreso(Contrato)",required=True, default=datetime.date.today())
    direction = fields.Text("Ubicacion /  Direccion del centro de costo")
    datetime_accident = fields.Datetime("Fecha/Hora de Accidente", required=True, default=datetime.datetime.now())
    direct_boss = fields.Char("Nombre Jefe Directo")
    crash_site = fields.Text("Lugar del accidente")
    antiquity = fields.Integer("Antigüedad en el cargo")
    antiquity_company = fields.Integer("Antigüedad en la empresa")
    affected_part = fields.Char("Parte del cuerpo afectada")
    injury_cause = fields.Char("Agente causante de la lesion(equipo, maquinaria, maeriales)")
    preexistence = fields.Char("Preexistencias")
    witness_ids = fields.One2many("initial.investigation.witness", "investigation_id", "Nombre Testigos")
    description = fields.Text("Descripcion del accidente")
    measure_ids = fields.One2many("initial.investigation.measure", "investigation_id", "Medidas de Control")
    signature = fields.Binary('Firma', copy=False)

    @api.model
    def create(self, vals):
        res = super(InitialInvestigation, self).create(vals)
        if res.name == 'Nuevo':
            sequence = self.env['ir.sequence'].search([('code', '=', 'sequence.initial.investigation')])
            res.name = sequence.next_by_id() or _('Nuevo')
        return res

    def action_confirm(self):
        for r in self:
            if not r.signature:
                raise UserError(_("Debe registrar la firma correspondiente del documento."))
            r.state = 'finished'
            if r.task_id:
                content, content_type = self.env.ref('project_task_form.action_report_initial_investigation')._render(r.id)
                self.env['ir.attachment'].create({
                    'name': r.task_id.name and _(r.name + " - %s.pdf", r.task_id.name) or _("Formulario de Investicacion Inicial.pdf"),
                    'type': 'binary',
                    'datas': base64.encodebytes(content),
                    'res_model': r.task_id._name,
                    'res_id': r.task_id.id
                })


class InitialInvestigationWitness(models.Model):
    _name = "initial.investigation.witness"

    investigation_id = fields.Many2one("initial.investigation", "Investigacion")
    witness_name = fields.Char("Nombre Testigo")


class InitialInvestigationMeasure(models.Model):
    _name = "initial.investigation.measure"

    investigation_id = fields.Many2one("initial.investigation", "Investigacion")
    action = fields.Char("Accion Correctiva / Preventiva")
    responsible = fields.Text("Responsables")
    date_init = fields.Date("Fecha Inicio", required=True, default=datetime.date.today())
    date_end = fields.Date("Fecha Fin", required=True, default=datetime.date.today())

