# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import datetime

class VisitForm(models.Model):
    _name = "visit.form"

    state = fields.Selection([('draft', 'Borrador'), ('finished', 'Completado')], string="Estado", default='draft')
    task_id = fields.Many2one('project.task', 'Tarea')
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company.id)
    date = fields.Date('Fecha', default=datetime.date.today())
    name = fields.Char("Nombre", default="Nuevo")
    social_reason = fields.Char("Razon Social")
    rut = fields.Char("RUT")
    client = fields.Char("Nombre de Cliente")
    community = fields.Char("Comuna")
    direction = fields.Text("Direccion")
    employee_number = fields.Integer("Numero de Empleados")
    direct_boss = fields.Char("Profesional Responsable")
    position = fields.Char("Cargo")
    objective_ids = fields.One2many('visit.form.objective', 'form_id', string='Objetivos')
    visit_result = fields.Text("Resultado de la Visita")
    signature = fields.Binary('Firma', copy=False)

    @api.model
    def create(self, vals):
        res = super(VisitForm, self).create(vals)
        if res.name == 'Nuevo':
            sequence = self.env['ir.sequence'].search([('code', '=', 'sequence.visit.form')])
            res.name = sequence.next_by_id() or _('Nuevo')
        return res

    def action_confirm(self):
        for r in self:
            if not r.signature:
                raise UserError(_("Debe registrar la firma correspondiente del documento."))
            r.state = 'finished'
            if r.task_id:
                content, content_type = self.env.ref('project_task_form.action_report_visit_form')._render(r.id)
                self.env['ir.attachment'].create({
                    'name': r.task_id.name and _(r.name + " - %s.pdf", r.task_id.name) or _("Formulario de Visita.pdf"),
                    'type': 'binary',
                    'datas': base64.encodebytes(content),
                    'res_model': r.task_id._name,
                    'res_id': r.task_id.id
                })


class VisitFormObjective(models.Model):
    _name = "visit.form.objective"

    form_id = fields.Many2one("visit.form", "Formulario de Visita")
    objective = fields.Char("Objetivo")

