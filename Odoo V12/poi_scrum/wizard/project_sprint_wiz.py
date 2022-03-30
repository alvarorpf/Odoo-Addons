# -*- encoding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ProjectSprintWiz(models.TransientModel):
    _name = 'project.sprint.wiz'

    project_id = fields.Many2one('project.project', 'Proyecto', required=True)

    def action_view(self):
        for r in self:
            if r.project_id:
                return {
                    'name': 'Sprints de Proyecto',
                    'domain': [('project_id', '=', r.project_id.id)],
                    'res_model': 'project.agile.scrum.sprint',
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'view_mode': 'kanban,tree,form',
                    'view_type': 'form',
                    'context': {
                        'default_project_id': r.project_id.id,
                    },
                }
            else:
                raise UserError('Debe seleccionar un proyecto para poder mostrar los sprints del mismo')