# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import dateutil.parser


class GeneralSchedule(models.Model):
    _name = "general.schedule"
    _auto = False

    project_id = fields.Many2one('project.project', 'Proyecto')
    stage_id = fields.Many2one('project.stage.base', 'Etapa de Proyecto')
    parent_id = fields.Many2one('project.stage.base', 'Etapa de Proyecto')
    type = fields.Selection([('macro', 'Macro'), ('normal', 'Normal')], string='Tipo de Tarea')
    name = fields.Char('Descripcion de Tarea')
    assigned_id = fields.Many2one('res.users', 'Asignado a')
    date_start = fields.Datetime('Fecha Inicio')
    date_deadline = fields.Datetime('Fecha Limite')
    state = fields.Selection([('pending', 'Pendiente'), ('completed', 'Completada'), ('rescheduled', 'Reprogramada'), ('developing', 'Desarrollo')],
                             string='Estado')
    progress = fields.Float('Progreso')

    def _select(self):
        select_str = """
            (select 
                    ps.project_id as project_id,
                    ps.project_stage_id as stage_id,
                    null as parent_id,
                    'macro' as type,
                    psb.name as name,
                    null as assigned_id,
                    DATE_TRUNC('second',TO_TIMESTAMP(concat(ps.date_start, ' ', '08:00'), 'YYYY-MM-DD HH24:MI')) at time zone 'gmt' as date_start,
                    DATE_TRUNC('second',TO_TIMESTAMP(concat(ps.date_end, ' ', '08:00'), 'YYYY-MM-DD HH24:MI')) at time zone 'gmt' as date_deadline,
                    '' as state,
                    (select 
                        avg(progress) 
                    from project_task as pt 
                    where pt.project_id = ps.project_id and pt.project_stage_id = ps.project_stage_id and pt.view_cg = true) as progress
                from project_stage as ps
                inner join project_stage_base as psb on ps.project_stage_id = psb.id
                order by ps.id)
                union all
                (select 
                    pt.project_id as project_id,
                    pt.project_stage_id as stage_id, 
                    pt.project_stage_id as parent_id, 
                    'normal' as type,
                    pt.name as name,
                    user_id as assigned_id,
                    pt.date_start as date_start,
                    pt.date_deadline as date_deadline,
                    pt.state as state,
                    pt.progress as progress
                from project_task as pt
                where pt.view_cg = true and pt.task_type = 'general')
                union all
                (select 
                    pt.project_id as project_id,
                    pt.project_stage_id as stage_id, 
                    pt.project_stage_id as parent_id, 
                    'normal' as type,
                    pt.name as name,
                    user_id as assigned_id,
                    pt.date_start as date_start,
                    pt.date_deadline as date_deadline,
                    'developing' as state,
                    pt.progress as progress
                from project_task as pt
                where pt.view_cg = true and pt.task_type = 'developing')
                order by stage_id, date_start
        """
        return select_str

    @api.model_cr
    def init(self):
        table = "genera_schedule"
        self.env.cr.execute("""
                DROP VIEW IF EXISTS general_schedule;
                CREATE OR REPLACE VIEW general_schedule as (
                SELECT row_number() over() as id, *
                    FROM(
                    %s 
                    ) as asd
                )""" % self._select())


class StatusGeneralSchedule(models.AbstractModel):
    _name = 'report.poi_scrum.template_status_general_schedule'

    @api.multi
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('poi_scrum.template_status_general_schedule')
        projects = self.env['project.project'].browse(docids)
        data = []
        docs = []
        for p in projects:
            for ps in p.project_stage_ids:
                if ps.project_stage_id.is_dev:
                    info = {
                        'id': ps.id,
                        'name': ps.project_stage_id.name,
                        'assigned_id': '',
                        'task_type': 'Developing',
                        'date_start': ps.date_start,
                        'date_end': ps.date_end,
                        'date_deadline': ps.date_end,
                        'project_date_end': p.end_date,
                        'parent_id': '',
                        'description': ps.observation or '',
                        'progress': round(ps.progress,2),
                        'depend_id': '',
                    }
                    docs.append(info)
                else:
                    info = {
                        'id': ps.id,
                        'name': ps.project_stage_id.name,
                        'assigned_id': '',
                        'task_type': 'Macro',
                        'date_start': ps.date_start,
                        'date_end': ps.date_end,
                        'date_deadline': ps.date_end,
                        'project_date_end': p.end_date,
                        'parent_id': '',
                        'description': ps.observation or '',
                        'progress': round(ps.progress, 2),
                        'depend_id': '',
                    }
                    docs.append(info)
                    tasks = self.env['project.task'].search([('project_id', '=', p.id), ('project_stage_id', '=', ps.project_stage_id.id), ('view_cg', '=', True)])
                    if tasks:
                        for t in tasks:
                            if t.date_start and t.date_deadline:
                                info = {
                                    'id': t.id,
                                    'name': t.name,
                                    'assigned_id': t.user_id.name or '',
                                    'task_type': 'Normal',
                                    'date_start': dateutil.parser.parse(str(t.date_start)).date(),
                                    'date_end': dateutil.parser.parse(str(t.date_deadline)).date(),
                                    'date_deadline': dateutil.parser.parse(str(t.date_deadline)).date(),
                                    'project_date_end': p.end_date,
                                    'parent_id': ps.id,
                                    'description': t.name or '',
                                    'progress': round(t.progress, 2),
                                    'depend_id': t.parent_id.id or '',
                                }
                                docs.append(info)
            data.append({'project': p, 'docs': docs})
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'data': data,
            'company_id': self.env.user.company_id,
        }