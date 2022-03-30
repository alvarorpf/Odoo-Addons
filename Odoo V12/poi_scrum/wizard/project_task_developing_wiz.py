# -*- encoding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ProjectTaskDevelopingWiz(models.TransientModel):
    _name = 'project.task.developing.wiz'

    project_id = fields.Many2one('project.project', 'Proyecto', required=True)

    def action_view(self):
        for r in self:
            if r.project_id:
                return {
                    'name': 'Tareas Desarrollo',
                    'domain': [('project_id', '=', r.project_id.id), ('task_type', '=', 'developing')],
                    'res_model': 'project.task',
                    'type': 'ir.actions.act_window',
                    'view_id': self.env.ref('poi_scrum.project_task_developing_tree_view').ids,
                    'view_mode': 'tree',
                    'view_type': 'form',
                    'context': {
                        'default_project_id': r.project_id.id,
                        'default_task_type': 'developing',
                        'default_project_stage_id': self.env.ref('poi_scrum.stage_developing').id,
                        'search_default_my_tasks': 1,
                    },
                }
            else:
                raise UserError('Debe seleccionar un proyecto para poder mostrar las tareas del mismo')