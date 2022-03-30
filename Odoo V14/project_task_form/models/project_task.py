# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = "project.task"

    count_forms = fields.Integer(compute='_compute_forms',)
    color = fields.Integer(string='Color', compute='_compute_color')

    def create_forms(self):
        return {
            'name': 'Crear formularios',
            'res_model': 'add.forms',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'target': 'new',
            'view_type': 'form',
            'context': {
                'default_task_id': self.id,
            }
        }

    def action_view_forms(self):
        for r in self:
            return {
                'name': 'Formularios',
                'res_id': False,
                'res_model': 'task.form.report',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'tree',
                'view_type': 'form',
                'domain': [('task_id', '=', r.id)],
                'context': {
                    'create': False,
                },
            }

    @api.depends('stage_id')
    def _compute_forms(self):
        for r in self:
            forms = self.env['task.form.report'].search([('task_id', '=', r.id)])
            count = len(forms)
            r.count_forms = count

    @api.depends('date_deadline', 'stage_id')
    def _compute_color(self):
        for r in self:
            if r.kanban_state == 'done':
                r.color = 10
            else:
                if r.date_deadline:
                    today = datetime.date.today()
                    res = today - r.date_deadline
                    if res.days > 0:
                        r.color = 1
                    elif 0 >= res.days > -3:
                        r.color = 3
                    else:
                        r.color = 4
                else:
                    r.color = 0


class ProjectStage(models.Model):
    _inherit = "project.task.type"

    has_initial_investigation = fields.Boolean('Form. Investigacion Inicial')
    has_investigation_report = fields.Boolean('Rep. Investigacion de Accidentes')
    has_visit_form = fields.Boolean('Form. de Visita')
    has_election_form = fields.Boolean('Acta de Elecciones')
    has_security_inspection = fields.Boolean('Form. de Inpeccion de Seguridad')
    has_observation_form = fields.Boolean('Form. Observacion de Conducta')
