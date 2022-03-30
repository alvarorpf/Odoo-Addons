# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import datetime


class ElectionForm(models.Model):
    _name = "election.form"

    name = fields.Char("Nombre", default="Nuevo")
    state = fields.Selection([('draft', 'Borrador'), ('finished', 'Completado')], string="Estado", default='draft')
    task_id = fields.Many2one('project.task', 'Tarea')
    community = fields.Char('Comuna')
    date = fields.Date('Fecha', default=datetime.date.today())
    date_election = fields.Date('Fecha Eleccion', required=True, default=datetime.date.today())
    social_reason = fields.Char('Razon Social')
    rut = fields.Char('RUT')
    project_id = fields.Many2one('project.project', "Centro de costo")
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company.id)
    direction = fields.Text('Direccion')
    suffrage_ids = fields.One2many('election.form.suffrage', 'form_id', 'Votos emitidos')
    votes_count = fields.Integer('Votos Escrutados')
    votes_null = fields.Integer('Votos Nulos')
    votes_total = fields.Integer('Total de Votos')
    headline_ids = fields.One2many('election.form.headline', 'form_id', 'Titulares')
    substitute_ids = fields.One2many('election.form.substitute', 'form_id', 'Suplentes')
    witness_ids = fields.One2many('election.form.witness', 'form_id', 'Testigos')
    note = fields.Text('Notas Adicionales')

    @api.model
    def create(self, vals):
        res = super(ElectionForm, self).create(vals)
        if res.name == 'Nuevo':
            sequence = self.env['ir.sequence'].search([('code', '=', 'sequence.election.form')])
            res.name = sequence.next_by_id() or _('Nuevo')
        return res

    def action_confirm(self):
        for r in self:
            r.state = 'finished'
            if r.task_id:
                content, content_type = self.env.ref('project_task_form.action_report_election_form')._render(r.id)
                self.env['ir.attachment'].create({
                    'name': r.task_id.name and _(r.name + " - %s.pdf", r.task_id.name) or _(
                        "Acta de Eleccion.pdf"),
                    'type': 'binary',
                    'datas': base64.encodebytes(content),
                    'res_model': r.task_id._name,
                    'res_id': r.task_id.id
                })


class ElectionFormSuffrage(models.Model):
    _name = "election.form.suffrage"

    form_id = fields.Many2one('election.form', 'Formulario de Eleccion')
    name = fields.Char("Nombre")
    rut = fields.Char('RUT')
    votes = fields.Integer('Votos')


class ElectionFormHeadline(models.Model):
    _name = "election.form.headline"

    form_id = fields.Many2one('election.form', 'Formulario de Eleccion')
    name = fields.Char("Nombre")
    rut = fields.Char('RUT')


class ElectionFormSubstitute(models.Model):
    _name = "election.form.substitute"

    form_id = fields.Many2one('election.form', 'Formulario de Eleccion')
    name = fields.Char("Nombre")
    rut = fields.Char('RUT')


class ElectionFormWitness(models.Model):
    _name = "election.form.witness"

    form_id = fields.Many2one('election.form', 'Formulario de Eleccion')
    name = fields.Char("Nombre")
    rut = fields.Char('RUT')
    signature = fields.Binary('Firma', copy=False)

