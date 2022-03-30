# coding=utf-8
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class Sprint(models.Model):
    _inherit = "project.agile.scrum.sprint"

    @api.depends('task_ids')
    def _compute_progress_hours(self):
        prog = 0.0
        for sprint in self:
            if sprint.task_ids:
                for t in sprint.task_ids:
                    prog += t.progress
                if len(sprint.task_ids) > 0:
                    sprint.progress = round((prog / len(sprint.task_ids)), 2)
                else:
                    sprint.progress = prog
            else:
                sprint.progress = prog

    @api.multi
    @api.depends('user_id')
    def _compute_author(self):
        for s in self:
            if s.user_id:
                s.state_id = s.user_id.state_id.id
                s.department_id = s.user_id.department_id.id

    def _default_user_id(self):
        return self.env.user

    @api.multi
    @api.depends('state')
    def _compute_unfinished_task_ids(self):
        for record in self:
            if record.state != "completed":
                record.unfinished_task_ids = False
                return
            lista1 = self.env['project.task'].search([("sprint_ids", "in", record.id), ('stage_id.finish', '=', False)]).ids
            lista2 = self.env['project.task'].search([("sprint_ids", "in", record.id), ('sprint_id', '!=', record.id)]).ids
            for l in lista2:
                lista1.append(l)
            record.unfinished_task_ids = lista1

    @api.multi
    @api.depends('state')
    def _compute_finished_task_ids(self):
        for record in self:
            if record.state != "completed":
                record.finished_task_ids = self.env['project.task'].search([("sprint_id", "=", record.id)]).ids
            record.finished_task_ids = self.env['project.task'].search([("sprint_ids", "in", record.id), ("stage_id.finish", "=", True)]).ids

    @api.multi
    @api.depends("task_ids")
    def _compute_task_count(self):
        for record in self:
            list = self.env['project.task'].search([("sprint_ids", "in", record.id), ('sprint_id', '!=', record.id)]).ids
            list2 = self.env['project.task'].search([("sprint_id", "=", record.id)]).ids
            for l in list2:
                list.append(l)
            record.task_count = len(list)

    user_id = fields.Many2one('res.users', string="User", default=_default_user_id)
    start_date = fields.Datetime(default=fields.Datetime.now)
    project_id = fields.Many2one('project.project', string='Proyecto', required=True)
    name = fields.Char(default='Nuevo', readonly=True, store=True)
    progress = fields.Float("Progreso", compute='_compute_progress_hours')
    label_tasks = fields.Char(string='Tareas', default=lambda s: _('Tareas'))
    state_id = fields.Many2one(
        string=u'Regional',
        comodel_name='res.country.state',
        ondelete='set null',
        compute=_compute_author,
        store=True,
        default=lambda self: self.env.user.state_id,
        index=True)

    department_id = fields.Many2one(
        string=u'Area',
        comodel_name='hr.department',
        ondelete='set null',
        compute=_compute_author,
        store=True,
        default=lambda self: self.env.user.department_id,
        index=True)

    finished_task_ids = fields.Many2many(
        comodel_name="project.task",
        compute="_compute_finished_task_ids",
        string="Tareas Finalizadas",
    )

    @api.onchange('team_id', 'start_date')
    def _onchange_sprint_info(self):
        for r in self:
            if r.team_id and r.team_id.id:
                week_length = int(r.team_id.default_sprint_length)
                date = r.start_date + timedelta(days=week_length * 7)
                r.end_date = date

    @api.model
    def create(self, values):
        if values.get('name', 'Nuevo') == 'Nuevo':
            val = values.get('project_id')
            project = self.env['project.project'].search([('id', '=', val)])
            if project and project.id:
                count = project.sprint_count
                values['name'] = 'SP/' + str(count)
                project.sprint_count += 1
                record = super(Sprint, self).create(values)
                return record

    @api.multi
    def write(self, values):
        if 'state' in values:
            if self.state == 'active' and values['state'] == 'draft':
                raise UserError('El sprint no puede volver a un estado anterior.')
            if self.state == 'completed' and values['state'] == 'draft':
                raise UserError('El sprint no puede volver a un estado anterior.')
            if self.state == 'completed' and values['state'] == 'active':
                raise UserError('El sprint no puede volver a un estado anterior.')
            if self.state == 'draft' and values['state'] == 'completed':
                raise UserError('Para que un sprint pase a un estado completado, se debe realizar el flojo completo.')
            fexe = self._context.get('first_execution') or False
            if not fexe:
                if self.state == 'draft':
                    self.action_active()
        res = super(Sprint, self).write(values)
        return res

    @api.multi
    def action_active(self):
        for r in self:
            # sprint = self.env['project.agile.scrum.sprint'].search([('project_id', '=', r.project_id.id)])
            # s = sprint.filtered(lambda x: x.state == 'active')
            # if s:
            #     raise UserError('El proyecto ya cuenta con un sprint activo, debe finalizar el sprint para poder activar uno nuevo')
            if len(r.task_ids) > 0:
                r.with_context({'first_execution': True}).write({'state': 'active'})
                r.task_ids.action_assign_user()
            else:
                raise UserError('Debe adicionar al menos una tarea a este sprint para poder activarlo')

    @api.multi
    def action_complete(self):
        for r in self:
            r.task_ids.write({"sprint_ids": [(4, r.id)]})
            r.write({
                'state': 'completed',
                'actual_end_date': fields.Datetime.now()
            })

    @api.multi
    def open_tasks(self):
        self.ensure_one()
        action = self.env.ref_action(
            "project.act_project_project_2_project_task_all"
        )

        action['context'] = {
            'group_by': 'stage_id',
            'default_project_id': self.project_id.id,
            'default_sprint_id': self.id,
            'default_task_type': 'developing',
            'search_default_my_tasks': 1,
        }
        action['domain'] = [('project_id', '=', self.project_id.id), ('sprint_id', '=', self.id)]
        return action
