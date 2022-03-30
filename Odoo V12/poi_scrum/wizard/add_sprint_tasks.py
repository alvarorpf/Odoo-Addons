from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class AddSprintTasks(models.TransientModel):
    _name = 'add.sprint.tasks'
    _description = 'Adicionar tareas a Sprint'

    task_ids = fields.Many2many('project.task', string='Tareas')
    default_sprint = fields.Selection([('new', 'Nuevo'), ('exist', 'Existente')], 'Seleccionar', required=True, default='exist')
    sprint_id = fields.Many2one('project.agile.scrum.sprint', 'Sprint')
    project_id = fields.Many2one('project.project', string="Proyecto")
    date_start = fields.Datetime('Fecha Inicio')
    date_end = fields.Datetime('Fecha Fin')
    team_id = fields.Many2one('project.agile.team', 'Equipo')

    @api.model
    def default_get(self, fields):
        res = super(AddSprintTasks, self).default_get(fields)
        task_ids = self.env.context.get('active_ids', [])
        for t in self.env['project.task'].browse(task_ids):
            if self.project_id and self.project_id.id:
                if t.project_id.id == self.project_id.id:
                    raise UserError('Debe seleccionar las mismas tareas de un proyeto para asignarlas a un sprint')
            else:
                res['project_id'] = t.project_id.id
        res['task_ids'] = task_ids
        return res

    @api.onchange('project_id')
    def _get_info(self):
        for r in self:
            if r.project_id and r.project_id.team_ids:
                r.team_id = r.project_id.team_ids[0]
            return {
                'domain': {
                    'sprint_id':
                        [
                            ('project_id', '=', (self.project_id and self.project_id.id) or False), ('state', 'in', ['draft', 'active'])
                        ]
                }
            }

    @api.multi
    def action_add_tasks(self):
        for r in self:
            if r.default_sprint == 'exist':
                if r.sprint_id and r.task_ids:
                    for t in r.task_ids:
                        if t.task_type == 'developing':
                            if t.stage_id.finish:
                                raise UserError('No se puede adicionar una tarea finalizada a otro sprint')
                            t.sprint_id = r.sprint_id
                            t.team_id = r.sprint_id.team_id.id
                            if not t.user_id and r.sprint_id.state == 'active':
                                t.user_id = t.draft_assigned_id.id
                        else:
                            raise UserError('No se pueden añadir tareas de tipo general a un sprint. Tarea: %s' % t.name)
            elif r.default_sprint == 'new':
                sprint = self.env['project.agile.scrum.sprint']
                s = sprint.create({
                    'project_id': r.project_id and r.project_id.id or False,
                    'team_id': r.team_id and r.team_id.id or False,
                    'start_date': r.date_start,
                    'end_date': r.date_end
                })
                if s.id and r.task_ids:
                    for t in r.task_ids:
                        if t.task_type == 'developing':
                            if t.stage_id.finish:
                                raise UserError('No se puede adicionar una tarea finalizada a otro sprint')
                            t.sprint_id = s.id
                            t.team_id = r.team_id.id
                        else:
                            raise UserError('No se pueden añadir tareas de tipo general a un sprint. Tarea: %s' % t.name)
