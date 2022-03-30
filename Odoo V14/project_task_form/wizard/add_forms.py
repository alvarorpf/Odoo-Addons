# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountClosingWizard(models.TransientModel):
    _name = 'add.forms'
    _description = 'Adicion de formularios'

    task_id = fields.Many2one("project.task", "Tarea")

    has_initial_investigation = fields.Boolean(related="task_id.stage_id.has_initial_investigation")
    has_investigation_report = fields.Boolean(related="task_id.stage_id.has_investigation_report")
    has_visit_form = fields.Boolean(related="task_id.stage_id.has_visit_form")
    has_election_form = fields.Boolean(related="task_id.stage_id.has_election_form")
    has_security_inspection = fields.Boolean(related="task_id.stage_id.has_security_inspection")
    has_observation_form = fields.Boolean(related="task_id.stage_id.has_observation_form")

    initial_investigation = fields.Boolean('Form. Investigacion Inicial')
    investigation_report = fields.Boolean('Rep. Investigacion de Accidentes')
    visit_form = fields.Boolean('Form. de Visita')
    election_form = fields.Boolean('Acta de Elecciones')
    security_inspection = fields.Boolean('Form. de Inpeccion de Seguridad')
    observation_form = fields.Boolean('Form. Observacion de Conducta')

    def action_confirm(self):
        for r in self:
            form_id = False
            if r.visit_form:
                form_id = self.env['visit.form'].create({
                    'task_id': r.task_id.id or False
                })
            if r.initial_investigation:
                form_id = self.env['initial.investigation'].create({
                    'task_id': r.task_id.id,
                    'project_id': r.task_id.project_id and r.task_id.project_id.id or False
                })
            if r.initial_investigation:
                form_id = self.env['investigation.report'].create({
                    'task_id': r.task_id.id,
                    'project_id': r.task_id.project_id and r.task_id.project_id.id or False
                })
            if r.security_inspection:
                form_id = self.env['security.inspection'].create({
                    'task_id': r.task_id.id,
                    'project_id': r.task_id.project_id and r.task_id.project_id.id or False
                })
            if r.election_form:
                form_id = self.env['election.form'].create({
                    'task_id': r.task_id.id,
                    'project_id': r.task_id.project_id and r.task_id.project_id.id or False
                })
            if r.observation_form:
                form_id = self.env['observation.form'].create({
                    'task_id': r.task_id.id,
                    'project_id': r.task_id.project_id and r.task_id.project_id.id or False
                })
            if not form_id:
                raise UserError("Debe seleccionar al menos un formulario para ser creado.")
        return {
                'name': 'Formularios',
                'res_id': False,
                'res_model': 'task.form.report',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'tree',
                'view_type': 'form',
                'domain': [('task_id', '=', r.task_id.id)],
                'context': {
                        'create': False,
                },
            }