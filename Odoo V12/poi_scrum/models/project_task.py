# coding=utf-8
from odoo import models, fields, api, tools, _
import collections
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import timedelta

TRACK_FIELD_CHANGES = set(('stage_id', 'user_id', 'state'))


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    count = fields.Boolean('Contabilizar', help='Contabilizar las horas de esta etapa en una tarea')
    finish = fields.Boolean('Etapa de Finalización')


class ProjectTaskType2(models.Model):
    _inherit = 'project.task.type2'

    icon = fields.Char('Icono')


class Task(models.Model):
    _inherit = "project.task"
    _order = 'date_start asc'

    @api.multi
    @api.depends('project_id')
    def _compute_stage_id(self):
        for r in self:
            if r.project_id:
                if r.task_type == 'developing':
                    r.project_stage_id = self.env.ref('poi_scrum.stage_developing').id
                else:
                    r.project_stage_id = r.project_id.stage_id.id
                if r.project_id.team_ids:
                    r.team_id = r.project_id.team_ids[0]

    @api.depends('date_start', 'date_deadline')
    def _compute_color(self):
        for r in self:
            if r.stage_id.finish:
                r.color = 0
            else:
                if r. date_start and r.date_deadline:
                    if r.date_start == r.date_deadline:
                        r.color = 1
                    else:
                        date = r.date_deadline.date()
                        d_deadline = r.date_deadline + timedelta(days=1)
                        d_deadline = d_deadline.date()
                        d_prev = r.date_deadline - timedelta(days=1)
                        d_prev = d_prev.date()
                        d_actual = fields.Datetime.now().date()
                        if d_actual < d_prev:
                            r.color = 10
                        elif d_actual == d_prev or d_actual == date:
                            r.color = 3
                        elif d_deadline >= d_actual:
                            r.color = 1

    @api.multi
    @api.depends('user_id')
    def _compute_author(self):
        for s in self:
            if s.user_id:
                s.state_id = s.user_id.state_id.id
                s.department_id = s.user_id.department_id.id
    
    @api.multi
    @api.depends('user_id', 'assigned_ids')
    def _compute_assigned_to_me(self):
        for task in self:
            task.assigned_to_me = (task.user_id.id == self.env.user.id) or (self.env.user.id in task.assigned_ids.ids)

    draft_assigned_id = fields.Many2one('res.users', 'Asignación Borrador a')
    state = fields.Selection([('pending', 'Pendiente'), ('completed', 'Completada'), ('rescheduled', 'Reprogramada')],
                             string='Estado', default='pending')
    observations = fields.Text(string='Observaciones')
    project_stage_id = fields.Many2one('project.stage.base', string="Etapa de Proyecto", compute='_compute_stage_id',
                                       store=True, readonly=False)
    task_type = fields.Selection([('general', 'General'), ('developing', 'Desarrollo')], default='general')
    view_cg = fields.Boolean('Ver en cronograma general', default=True)
    task_log_ids = fields.One2many('project.task.log', 'task_id')
    task_log_count = fields.Integer(compute='_compute_task_log_count')
    finish = fields.Boolean(related='stage_id.finish', readonly=True, store=True)
    user_ids = fields.Many2many(comodel_name="res.users", column1="task_id", column2="user_id", string="Historia de Usuario Asignado",)
    date_deadline = fields.Datetime('Fecha Límite')
    team_id = fields.Many2one('project.agile.team', string='Equipo', compute='_compute_stage_id', store=True, readonly=False)
    color = fields.Integer(string='Color', compute='_compute_color')
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
    assigned_ids = fields.Many2many('res.users', 'task_assigned_rel', 'task_id', 'assigned_user_id', string='Otros Asignados', track_visibility='onchange')

    @api.depends('task_log_ids')
    def _compute_task_log_count(self):
        for task in self:
            task.task_log_count = len(task.task_log_ids)

    @api.multi
    def _get_changed_fields(self, field_names, vals):
        changes = collections.defaultdict(dict)
        changed_fields = set(field_names) & set(vals.keys())
        if changed_fields:
            for record in self:
                for field in changed_fields:
                    old_value = record[field]
                    new_value = self._fields[field].convert_to_record(
                        self._fields[field].convert_to_cache(
                            vals[field], self),
                        self)
                    if old_value != new_value:
                        changes[record.id][field] = (old_value, new_value)
        return dict(changes)

    @api.model
    def create(self, values):
        if 'project_stage_id' in values and 'project_id' in values:
            stage = self.env['project.stage'].search([('project_id', '=', values['project_id']), ('project_stage_id', '=', values['project_stage_id'])])
            if stage:
                if stage.allow_tasks:
                    date_start = stage.date_start
                    date_end = stage.date_end
                    date_actual = datetime.strptime(values['date_start'], '%Y-%m-%d %H:%M:%S').date()
                    if not (date_start <= date_actual <= date_end):
                        raise UserError('No se pueden crear tareas fuera de fechas según configuración del proyecto')
                    if 'date_deadline' in values:
                        date_dealine = datetime.strptime(values['date_deadline'], '%Y-%m-%d %H:%M:%S').date()
                        if date_dealine > date_end:
                            raise UserError('No se pueden crear tareas con una fecha límite mayor a la establecida en la configuración del proyecto')
                if stage.view_cg:
                    values['view_cg'] = True
            else:
                raise UserError('No se encuentra la configuracion de la etapa del proyecto')
        else:
            raise UserError('Debe seleccionar un proyecto y su etapa correspondiente para poder crear la tarea.')
        record = super(Task, self).create(values)
        if record.user_id:
            record.write({"user_ids": [(4, record.user_id.id)]})
        record._reg_log()
        if record.sprint_id:
            if record.sprint_id.state == 'active':
                record.user_id = record.draft_assigned_id
                record.team_id = record.sprint_id.team_id
        return record

    @api.multi
    def write(self, vals):
        changes = self._get_changed_fields(TRACK_FIELD_CHANGES, vals)
        updates = collections.defaultdict(dict)
        for task in self:
            if task.task_type == 'developing':
                if 'stage_id' in vals:
                    if task.sprint_id:
                        if task.sprint_id.state != 'active':
                            raise UserError('La tarea no puede pasar de etapas mientras esta no se encuentre en un sprint activo.')
                    else:
                        raise UserError(
                            'La tarea no se encuentra en un sprint.')
            if task.id in changes:
                updates[task.id] = self._preprocess_write_changes(changes[task.id])
        res = super(Task, self).write(vals)
        return res

    def action_complete(self):
        for r in self:
            fexe = self._context.get('first_execution') or False
            if fexe:
                r.progress = 100
                r.date_end = fields.Datetime.now()
            else:
                r.state = 'completed'
                r.progress = 100
                r.date_end = fields.Datetime.now()

    def action_reschedule(self):
        for r in self:
            r.state = 'rescheduled'

    def action_assign_user(self):
        for r in self:
            if r.draft_assigned_id:
                r.user_id = r.draft_assigned_id and r.draft_assigned_id.id
            else:
                raise UserError('Debe realizar la asignación previa de un usuario a la tarea %s' % r.name)

    def _reg_log(self, stage=False, state=False, user=False, observations=''):
        for r in self:
            stage = stage if stage else r.stage_id
            state = state if state else r.state
            user = user if user else r.user_id
            task_log = self.env['project.task.log']
            if r.task_type == 'general':
                task_log.create({
                    'task_id': r.id or False,
                    'user_id': self.env.user.id or False,
                    'state': state,
                    'assigned_id': user and user.id or False,
                    'date_prev': fields.Datetime.now(),
                    'task_type': r.task_type,
                    'observations': observations,
                })
            elif r.task_type == 'developing':
                task_log.create({
                    'task_id': r.id or False,
                    'user_id': self.env.user.id or False,
                    'stage_id': stage and stage.id or False,
                    'assigned_id': user and user.id or False,
                    'date_prev': fields.Datetime.now(),
                    'task_type': r.task_type,
                    'observations': observations,
                })

    def _preprocess_write_changes(self, changes):
        vals = {}
        for r in self:
            if 'user_id' in changes:
                log = r.task_log_ids.filtered(
                    lambda x: x.assigned_id.id == r.user_id.id and x.stage_id.id == r.stage_id.id)
                if log:
                    log[0].date = fields.Datetime.now()
                if r.stage_id.count:
                    raise UserError('Para asignar un nuevo usuario a esta tarea en una etapa en la que se contabilizan las horas primero debera poner la etapa en pausa.')
                else:
                    vals['user_id'] = changes['user_id'][1]
                    r.write({"user_ids": [(4, changes['user_id'][1].id)]})
                    r._reg_log(user=changes['user_id'][1], observations='Asignación de usuario')
            if 'stage_id' in changes:
                old_stage, new_stage = changes['stage_id']
                log = r.task_log_ids.filtered(lambda x: x.assigned_id.id == r.user_id.id and x.stage_id.id == old_stage.id)
                if log:
                    log[0].date = fields.Datetime.now()
                if old_stage.count:
                    r.timesheet_ids.create({
                        'task_id': r.id or False,
                        'project_id': r.project_id.id or False,
                        'date': fields.Datetime.now(),
                        'user_id': r.user_id.id,
                        'name': 'Registro de horas en etapa %s' % old_stage.name,
                        'unit_amount': log[0].time_spent_calendar,
                    })
                    log_obj = self.env['project.task.log']
                    if len(r.assigned_ids) > 0:
                        for a in r.assigned_ids:
                            log_obj.create({
                                'task_id': r.id or False,
                                'user_id': self.env.user.id or False,
                                'stage_id': old_stage and old_stage.id or False,
                                'assigned_id': a and a.id or False,
                                'date_prev': log[0].date_prev,
                                'date': log[0].date,
                                'task_type': r.task_type,
                                'observations': 'Cambio de Etapa',
                            })
                if new_stage.finish:
                    r.date_end = fields.Datetime.now()
                    r.progress = 100
                vals['stage_id'] = new_stage
                r._reg_log(stage=new_stage, observations='Cambio de etapa')
            if 'state' in changes:
                old_state, new_state = changes['state']
                log = r.task_log_ids.filtered(
                    lambda x: x.assigned_id.id == r.user_id.id and x.state == old_state)
                if log:
                    log[0].date = fields.Datetime.now()
                vals['state'] = new_state
                if new_state == 'completed':
                    self.with_context({'first_execution': True}).action_complete()
                r._reg_log(state=new_state, observations='Cambio de estado')
            return vals

    @api.multi
    def view_actual_task(self):
        for r in self:
            return {
                'name': 'Tarea Desarrollo',
                'res_model': 'project.task',
                'res_id': r.id,
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
            }

    def action_subtask(self):
        action = super(Task, self).action_subtask()
        ctx = self.env.context.copy()
        ctx.update({
            'default_parent_id': self.id,
            'default_project_id': self.env.context.get('project_id', self.project_id.id),
            'default_name': self.env.context.get('name', self.name) + ':',
            'default_partner_id': self.env.context.get('partner_id', self.partner_id.id),
            'default_task_type': self.env.context.get('task_type', self.task_type),
        })
        action['context'] = ctx
        return action

    @api.multi
    def action_view_add_user(self):
        context = dict(self.env.context or {})
        context['default_task_id'] = self.id
        return {
            'name': _('Agregar Usuarios'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task.adduser.wiz',
            'view_id': self.env.ref('poi_scrum.project_task_adduser_wiz_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }