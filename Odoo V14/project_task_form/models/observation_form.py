# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import datetime

class ObservationForm(models.Model):
    _name = "observation.form"

    name = fields.Char("Nombre", default="Nuevo")
    state = fields.Selection([('draft', 'Borrador'), ('finished', 'Completado')], string="Estado", default='draft')
    task_id = fields.Many2one('project.task', 'Tarea')
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company.id)
    date = fields.Date('Fecha', default=datetime.date.today())
    datetime = fields.Datetime('Fecha/Hora', required=True, default=datetime.datetime.now())
    project_id = fields.Many2one('project.project', "Centro de costo")
    supervisor = fields.Char('Supervisor')
    supervisor_charge = fields.Char('Cargo')
    planned_hours = fields.Float("Tiempo Ocupado")

    employee = fields.Char('Nombre Trabajador Observado')
    antiquity = fields.Integer("Antigüedad en el cargo")
    antiquity_company = fields.Integer("Antigüedad en la empresa")
    charge = fields.Char('Cargo')
    type = fields.Selection([('with', 'Con aviso'), ('without', 'Sin Aviso')], string='Tipo de Observacion')
    reason = fields.Selection([
        ('repeated', 'Accidentes Repetidos'),
        ('reckless', 'Trabajador Temerario'),
        ('deficient', 'Desempeño deficiente'),
        ('critical', 'Trabajo Critico'),
        ('trouble', 'Problemas de habilidad'),
        ('work', 'Labores fuera de contrato'),
        ('new', 'Trabajador Nuevo'),
        ('other', 'Otro'),
    ], string="Motivo de la observacion")
    other_reason = fields.Char('Otro Motivo')
    area = fields.Char('Area o trabajo observado')
    line_ids = fields.One2many('observation.form.line', 'form_id', 'Observaciones')
    spotlight_ids = fields.One2many('observation.form.spotlight', 'form_id', 'Focos de Observacion')
    action_ids = fields.One2many('observation.form.action', 'form_id', 'Acciones')
    note = fields.Text('Comentarios')
    signature = fields.Binary('Firma', copy=False)

    @api.model
    def create(self, vals):
        res = super(ObservationForm, self).create(vals)
        if res.name == 'Nuevo':
            sequence = self.env['ir.sequence'].search([('code', '=', 'sequence.observation.form')])
            res.name = sequence.next_by_id() or _('Nuevo')
        return res

    def action_confirm(self):
        for r in self:
            if not r.signature:
                raise UserError(_("Debe registrar la firma correspondiente del documento."))
            r.state = 'finished'
            if r.task_id:
                content, content_type = self.env.ref('project_task_form.action_report_observation_form')._render(r.id)
                self.env['ir.attachment'].create({
                    'name': r.task_id.name and _(r.name + " - %s.pdf", r.task_id.name) or _(
                        "Formulario de Observacion.pdf"),
                    'type': 'binary',
                    'datas': base64.encodebytes(content),
                    'res_model': r.task_id._name,
                    'res_id': r.task_id.id
                })


class ObservationFormLine(models.Model):
    _name = "observation.form.line"

    form_id = fields.Many2one('observation.form', 'Formulario')
    observation = fields.Char('Observacion')


class ObservationFormSpotlight(models.Model):
    _name = "observation.form.spotlight"

    form_id = fields.Many2one('observation.form', 'Formulario')
    spotlight = fields.Char('Foco de Observacion')
    good_practice = fields.Char('Buenas Practicas')
    bad_practice = fields.Char('Malas Practicas')


class ObservationFormAction(models.Model):
    _name = "observation.form.action"

    form_id = fields.Many2one('observation.form', 'Formulario')
    action = fields.Char('Accion')
    ac_ap = fields.Selection([('ac', 'AC'), ('ap', 'AP')], string='AC/AP')
    responsible = fields.Char('Responsable')
    date_limit = fields.Date('Fecha Limite', required=True, default=datetime.date.today())
