# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import collections

TRACK_FIELD_CHANGES = set(('stage_id', 'owner_id', 'supervisor_id', 'health', 'origin_id'))


class ProjectType(models.Model):
    _name = "project.priority"

    name = fields.Char('Nombre')


class ProjectSponsor(models.Model):
    _name = "project.sponsor"

    name = fields.Char('Nombre')


class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = {'project.project', 'mail.activity.mixin'}

    @api.depends('deviation', 'pause', 'dismissed')
    def _compute_health(self):
        for r in self:
            if r.advance == 0.0:
                r.health = 'draft'
                r.color = 0
            else:
                if r.deviation <= 10:
                    r.health = 'in_term'
                    r.color = 10
                elif 10 <= r.deviation <= 20:
                    r.health = 'alert'
                    r.color = 3
                elif r.deviation >= 20:
                    r.health = 'delay'
                    r.color = 1
            if r.pause:
                r.health = 'pause'
                r.color = 2
            if r.dismissed:
                r.health = 'dismissed'
                r.color = 11
            if r.advance == 100.0 and r.end_stage:
                r.health = 'production'
                r.color = 4

    @api.depends('project_stage_ids')
    def _compute_advance(self):
        for r in self:
            advance = 0.0
            count = 0
            if r.project_stage_ids:
                for p in r.project_stage_ids:
                    advance += p.progress
                    count += 1
                r.advance = advance / count
            else:
                r.advance = advance

    @api.depends('start_date', 'end_date')
    def _compute_delay_days(self):
        for r in self:
            if r.advance != 0.0 or r.advance != 100.0:
                calendar = r.resource_calendar_id
                today = fields.Datetime.now()
                date_end = r.end_date
                if date_end:
                    hours = calendar.get_work_hours_count(start_dt=date_end, end_dt=today, compute_leaves=True)
                    days = hours / calendar.hours_per_day
                    r.delay_days = days

    @api.depends('advance', 'delay_days')
    def _compute_deviation(self):
        for r in self:
            if r.advance and r.delay_days:
                if r.deviation == 100.0:
                    r.deviation = 0
                else:
                    calendar = r.resource_calendar_id
                    hours = calendar.get_work_hours_count(start_dt=r.start_date, end_dt=r.end_date, compute_leaves=True)
                    days = hours / calendar.hours_per_day
                    if days > 0:
                        r.deviation = (r.delay_days / days) * (100 - r.advance)
                    else:
                        r.deviation = (r.delay_days) * (100 - r.advance)
            else:
                r.deviation = 0
    @api.depends('project_stage_ids')
    def _compute_dates(self):
        for r in self:
            if r.project_stage_ids:
                validation = 0
                for p in r.project_stage_ids:
                    if p.date_start and p.date_end:
                        validation = 1
                    else:
                        validation = 0
                if validation == 1:
                    ds = sorted(r.project_stage_ids, key=lambda r: r.date_start)[0]
                    de = sorted(r.project_stage_ids, key=lambda r: r.date_end, reverse=True)[0]
                    if ds.date_start and de.date_end:
                        r.start_date = datetime.combine(ds.date_start, fields.Datetime.now().time())
                        r.end_date = datetime.combine(de.date_end, fields.Datetime.now().time())

    @api.multi
    @api.depends('owner_id')
    def _compute_author(self):
        for s in self:
            if s.owner_id:
                s.department_id = s.owner_id.id

    icon = fields.Char('icon')
    allow_workflow = fields.Boolean(
        string='Permitir flujo de trabajo?',
        default=True,
    )
    agile_enabled = fields.Boolean(
        string='Use Agile',
        help='If checked project will be enabled for agile management',
        default=True
    )
    priority_id = fields.Many2one('project.priority', string='Prioridad')
    advance = fields.Float(string='Avance (%)', default=0.0)
    deviation = fields.Float(string='Desviación (%)', default=0.0)
    color = fields.Integer(string='Color')
    delay_days = fields.Integer(string='Días de Retraso', default=0)
    start_date = fields.Datetime(string='Fecha Inicio')
    end_date = fields.Datetime(string='Fecha Fin')
    description = fields.Text(string='Descripción')
    supervisor_id = fields.Many2one('res.users', string='Supervisor')
    supervisor_ids = fields.Many2many('res.users',
                                      'project_supervisor_rel',
                                      'project_id',
                                      'supervisor_id',
                                      string='Supervisores Involucrados')
    sponsor_ids = fields.Many2many('project.sponsor', string='Sponsor')
    area_id = fields.Many2one('hr.department', string='Área Solicitante')
    owner_id = fields.Many2one('hr.department', string='Dueño')
    requesting_user_id = fields.Many2one('res.users', string="Usuario Solicitante")
    sprint_count = fields.Integer('Contador de Sprints', default=1)
    health = fields.Selection(
        [('in_term', 'En Plazo'), ('alert', 'Alerta'), ('delay', 'Retraso'), ('pause', 'Pausado'), ('dismissed', 'Desestimado'), ('draft', 'Sin Iniciar'), ('production', 'En Producción')], string='Salud', store=True)
    project_stage_ids = fields.One2many('project.stage', 'project_id', string='Etapas de Proyecto')
    stage_id = fields.Many2one('project.stage.base', string="Etapa", ondelete="restrict", copy=False,
                               group_expand='_read_group_stage_ids')
    end_stage = fields.Boolean(related='stage_id.end_stage', string='Etapa Final')
    pause = fields.Boolean('Pausar Proyecto')
    dismissed = fields.Boolean('Desestimar Proyecto')
    privacy_visibility = fields.Selection(default='followers')
    request_id = fields.Many2one('request.form', string='Formulario de Requerimiento')
    origin_id = fields.Many2one('project.origin', 'Origen del Proyecto')
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

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['project.stage.base'].search([], order='sequence asc')
        return stages.browse([x.id for x in stage_ids])

    @api.model
    def create(self, values):
        project = super(ProjectProject, self.with_context(mail_create_nosubscribe=True)).create(values)
        project._compute_health()
        stages = self.env['project.stage.base'].search([])
        if stages:
            for s in stages:
                project.project_stage_ids = [(0, 0, {'project_id': project.id, 'project_stage_id': s.id})]
        init_stage = self.env.ref('poi_scrum.stage_planing').id
        project.stage_id = init_stage
        return project

    @api.model
    def _cron_update_info(self):
        projects = self.env['project.project'].search([])
        if projects:
            for p in projects:
                p._compute_dates()
                p._compute_advance()
                p._compute_delay_days()
                p._compute_deviation()
                p._compute_health()

    @api.multi
    def write(self, vals):
        changes = self._get_changed_fields(TRACK_FIELD_CHANGES, vals)
        updates = collections.defaultdict(dict)
        for project in self:
            if project.id in changes:
                updates[project.id] = self._preprocess_write_changes(changes[project.id])
        res = super(ProjectProject, self).write(vals)
        return res

    @api.multi
    def next_stage(self):
        for r in self:
            last_stage = self.env.ref('poi_scrum.stage_production').id
            log = self.env['project.log']
            if r.stage_id and r.stage_id.id != last_stage:
                stage = self.env['project.stage.base'].search([('sequence', '=', (r.stage_id.sequence + 1))])
                if stage:
                    r.stage_id = stage
                else:
                    raise UserError('Verifique las secuencias de las etapas para poder continuar.')
            else:
                raise UserError('El proyecto llego a su última etapa')

    @api.multi
    def open_tasks(self):
        for r in self:
            return {
                'name': 'Proyecto',
                'res_model': 'project.project',
                'res_id': r.id,
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
            }

    @api.multi
    def developing_tasks(self):
        self.ensure_one()
        action = self.env.ref_action(
            "project.act_project_project_2_project_task_all"
        )

        action['context'] = {
            'default_project_id': self.id,
            'default_task_type': 'developing',
            'search_default_my_tasks': 1,
        }
        views = [(self.env.ref('poi_scrum.project_task_developing_tree_view').id, 'tree'),
                 (self.env.ref('project.view_task_kanban').id, 'kanban'),
                 (self.env.ref('project.view_task_calendar').id, 'calendar'),
                 (self.env.ref('project.view_project_task_pivot').id, 'pivot'),
                 (self.env.ref('project.view_project_task_graph').id, 'graph'),
                 (self.env.ref('project.view_task_form2').id, 'form')]
        action['domain'] = [('project_id', '=', self.id), ('task_type', '=', 'developing')]
        action['views'] = views
        return action

    def action_view_log(self):
        return {
            'name': 'Log de Proyecto',
            'domain': [('project_id', '=', self.id), ('system_log', '=', False)],
            'res_model': 'project.log',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree',
            'view_type': 'form',
            'context': {}
        }

    def action_view_sprints(self):
        return {
            'name': 'Sprints',
            'domain': [('project_id', '=', self.id)],
            'res_model': 'project.agile.scrum.sprint',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'context': {}
        }

    def action_general_tasks(self):
        views = [(self.env.ref('poi_scrum.project_task_general_tree_view').id, 'tree'),
                 (self.env.ref('poi_scrum.view_general_task_kanban_scrum').id, 'kanban')]
        return {
            'name': 'Tareas Generales',
            'domain': [('project_id', '=', self.id), ('task_type', '=', 'general')],
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'views': views,
            'context': {
                'default_project_id': self.id,
                'default_task_type': 'general',
                'default_project_stage_id': self.stage_id and self.stage_id.id or False,
                'search_default_my_tasks': 1,
            },
        }

    def action_developing_tasks(self):
        views = [(self.env.ref('poi_scrum.project_task_developing_tree_view').id, 'tree'),
                 (self.env.ref('project.view_task_kanban').id, 'kanban'),
                 (self.env.ref('project.view_task_calendar').id, 'calendar'),
                 (self.env.ref('project.view_project_task_pivot').id, 'pivot'),
                 (self.env.ref('project.view_project_task_graph').id, 'graph'),
                 (self.env.ref('project.view_task_form2').id, 'form')]
        return {
            'name': 'Tareas Desarrollo',
            'domain': [('project_id', '=', self.id), ('task_type', '=', 'developing')],
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'views': views,
            'context': {
                'default_project_id': self.id,
                'default_task_type': 'developing',
                'default_project_stage_id': self.env.ref('poi_scrum.stage_developing').id,
                'search_default_my_tasks': 1,
            },
        }

    def action_general_schedule(self):
        for r in self:
            if r.start_date and r.end_date:
                return {
                    'name': 'Cronograma General',
                    'domain': [('project_id', '=', r.id)],
                    'res_model': 'general.schedule',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree',
                    'view_type': 'form',
                }
            else:
                raise UserError('Debe definir la fecha inicio y fecha fin de todas las etapas del proyecto.')

    def action_developing_schedule(self):
        for r in self:
            if r.start_date and r.end_date:
                return {
                    'name': 'Cronograma Desarrollo',
                    'domain': [('project_id', '=', r.id)],
                    'res_model': 'developing.schedule',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree',
                    'view_type': 'form',
                }
            else:
                raise UserError('Debe definir la fecha inicio y fecha fin de todas las etapas del proyecto.')

    def action_view_request(self):
        return {
            'name': 'Formulario de Requerimiento',
            'res_id': self.request_id.id,
            'res_model': 'request.form',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
        }

    def _reg_log(self, stage=False, health=False, owner=False, supervisor=False, observation=False, sys_log=False, origin=False):
        for r in self:
            stage = stage if stage else r.stage_id
            health = health if health else r.health
            owner = owner if owner else r.owner_id
            supervisor = supervisor if supervisor else r.supervisor_id
            origin = origin if origin else r.origin_id
            log = self.env['project.log']
            log.create({
                'project_id': r.id,
                'date': fields.Datetime.now(),
                'stage_id': stage and stage.id or False,
                'health': health,
                'owner_id': owner and owner.id or False,
                'supervisor_id': supervisor and supervisor.id or False,
                'deviation': r.deviation,
                'observation': observation or '',
                'system_log': sys_log,
                'origin_id': origin and origin.id or False
            })

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

    def _preprocess_write_changes(self, changes):
        vals = {}
        for r in self:
            if 'owner_id' in changes:
                vals['owner_id'] = changes['owner_id'][1]
                r._reg_log(owner=changes['owner_id'][1])
            if 'stage_id' in changes:
                vals['stage_id'] = changes['stage_id'][1]
                r._reg_log(stage=changes['stage_id'][1])
            # if 'pause' in changes:
            #     pause = changes['pause'][1]
            #     if pause:
            #         health = 'pause'
            #     else:
            #         if r.deviation <= 10:
            #             health = 'in_term'
            #         elif 10 <= r.deviation <= 20:
            #             health = 'alert'
            #         elif r.deviation >= 20:
            #             health = 'delay'
            #         else:
            #             health = ''
            #     vals['pause'] = pause
            #     r._reg_log(health=health)
            if 'supervisor_id' in changes:
                vals['supervisor_id'] = changes['supervisor_id'][1]
                r._reg_log(supervisor=changes['supervisor_id'][1])
            if 'origin_id' in changes:
                vals['origin_id'] = changes['origin_id'][1]
                r._reg_log(origin=changes['origin_id'][1])
            return vals

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        views = [(self.env.ref('mail.view_document_file_kanban').id, 'kanban'),
                 (self.env.ref('poi_scrum.view_attachment_tree_scrum').id, 'tree'),
                 (self.env.ref('base.view_attachment_form').id, 'form')]
        domain = [
            '|',
            '&', ('res_model', '=', 'project.project'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'project.task'), ('res_id', 'in', self.task_ids.ids)]
        return {
            'name': _('Documentos'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'views': views,
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }


class ProjectStages(models.Model):
    _name = 'project.stage'
    _order = 'id asc'

    def _compute_progress(self):
        for r in self:
            tasks = self.env['project.task'].search(
                [('project_id', '=', r.project_id.id), ('project_stage_id', '=', r.project_stage_id.id)])
            if tasks:
                progress = 0.0
                count = 0
                for t in tasks:
                    progress += t.progress
                    count += 1
                r.progress = progress / count
            else:
                r.progress = 0.0

    project_id = fields.Many2one('project.project', 'Proyecto')
    project_stage_id = fields.Many2one('project.stage.base', string='Etapa')
    res_user_ids = fields.Many2many('res.users', string='Responsables')
    date_start = fields.Date('Fecha Inicio')
    date_end = fields.Date('Fecha Fin')
    allow_tasks = fields.Boolean('Crear tareas dentro de fechas')
    view_cg = fields.Boolean('Ver tareas en cronograma general')
    sequence = fields.Integer(related='project_stage_id.sequence', string='Secuencia')
    observation = fields.Char('Observación')
    progress = fields.Float('Progreso', compute='_compute_progress')

    @api.multi
    def write(self, vals):
        res = super(ProjectStages, self).write(vals)
        for s in self:
            if (s.date_end and s.date_start) and (s.date_end < s.date_start):
                raise ValidationError('La Fecha Fin de la Etapa %s, no puede ser una fecha anterior a la fecha Inicio. ' % (s.project_stage_id.name))
        return res


class ProjectLog(models.Model):
    _name = 'project.log'

    project_id = fields.Many2one('project.project', string='Proyecto')
    date = fields.Date('Fecha de Actividad')
    stage_id = fields.Many2one('project.stage.base', string='Etapa')
    health = fields.Selection(
        [('in_term', 'En Plazo'), ('alert', 'Alerta'), ('delay', 'Retraso'), ('pause', 'Pausado'),
         ('dismissed', 'Desestimado'), ('draft', 'Sin Iniciar'), ('production', 'En Producción')], string='Salud')
    owner_id = fields.Many2one('hr.department', string='Dueño')
    supervisor_id = fields.Many2one('res.users', string='Supervisor')
    deviation = fields.Float(string='Desviación(%)')
    observation = fields.Char('Observación')
    system_log = fields.Boolean('Registro de Sistema', default=False)
    origin_id = fields.Many2one('project.origin', 'Origen del Proyecto')
