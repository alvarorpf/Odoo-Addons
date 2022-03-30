# coding=utf-8
from odoo import models, fields, api, tools, _


class ProjectTaskLog(models.Model):
    _name = 'project.task.log'
    _order = 'create_date DESC'
    @api.depends('stage_id', 'state')
    def _compute_name(self):
        for r in self:
            if r.state and not r.stage_id:
                if r.state == 'pending':
                    r.stage = 'Pendiente'
                elif r.state == 'completed':
                    r.stage = 'Completado'
                elif r.state == 'rescheduled':
                    r.stage = 'Reprogramada'
            elif r.stage_id and not r.state:
                r.stage = r.stage_id.name

    task_id = fields.Many2one('project.task', 'Tarea')
    user_id = fields.Many2one('res.users', string='Usuario Creador')
    stage = fields.Char('Etapa', compute='_compute_name', store=True)
    stage_id = fields.Many2one('project.task.type', string='Etapa de Tarea')
    state = fields.Selection([('pending', 'Pendiente'), ('completed', 'Completada'), ('rescheduled', 'Reprogramada')])
    assigned_id = fields.Many2one('res.users', string='Usuario Asignado')
    task_type = fields.Selection([('general', 'General'), ('developing', 'Desarrollo')], default='general')
    date_prev = fields.Datetime(required=True, index=True, readonly=True)
    date = fields.Datetime(required=True, index=True, readonly=True, default=fields.Datetime.now)
    task_time = fields.Float('Tiempo de Tarea')
    time_spent_total = fields.Float(readonly=True, compute='_compute_time_spent', store=True, string='Tiempo Total Utilizado')
    time_spent_calendar = fields.Float(readonly=True, compute='_compute_time_spent', store=True, string='Tiempo Total Calendario')
    calendar_id = fields.Many2one('resource.calendar', string='Tiempo de Trabajo', default=lambda self: self.env.user.company_id.resource_calendar_id.id)
    official_count = fields.Boolean(related='stage_id.count', store=True)
    observations = fields.Char('Observaciones')

    @api.depends('date_prev', 'date', 'calendar_id')
    def _compute_time_spent(self):
        for record in self:
            date_prev = fields.Datetime.from_string(record.date_prev)
            date = fields.Datetime.from_string(record.date)
            delta = date - date_prev
            record.time_spent_total = delta.total_seconds() / float(60 * 60)

            if record.calendar_id:
                working_hours = record.calendar_id.get_work_hours_count(
                    start_dt=date_prev,
                    end_dt=date,
                    compute_leaves=True)
                record.time_spent_calendar = working_hours
            else:
                record.time_spent_calendar = 0.0
