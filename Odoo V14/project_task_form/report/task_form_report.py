# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import UserError


class TaskFormReport(models.Model):
    _name = "task.form.report"
    _auto = False

    form = fields.Char('Número de Formulario')
    project_id = fields.Many2one('project.project', 'Centro de Costo')
    task_id = fields.Many2one('project.task', 'Tarea')
    date = fields.Date('Fecha de Registro')
    state = fields.Selection([('draft', 'Borrador'), ('finished', 'Completado')], string="Estado")
    company_id = fields.Many2one('res.company', 'Compañia')
    form_id = fields.Integer('ID de Formulario')
    model = fields.Char('Modelo de Formulario')
    types = fields.Selection([
        ('election', 'Acta de Eleccion'),
        ('initial', 'Investigacion Inicial'),
        ('investigation', 'Investigacion de Accidentes'),
        ('observation', 'Formulario de Observacion'),
        ('security', 'Formulario Inspeccion de Seguridad'),
        ('visit', 'Formulario de Visita'),
    ], string="Tipo de Formulario")
    title = fields.Char('Titulo de Formulario')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'task_form_report')
        query = """
            CREATE OR REPLACE VIEW task_form_report AS (
            select 
                row_number() over() as id,
                res.form,
                res.project_id,
                res.task_id,
                res.date,
                res.state,
                res.company_id,
                res.form_id,
                res.model,
                res.types,
                res.title
            from (
            (
            select 
                ef.name as form,
                pt.project_id as project_id ,
                ef.task_id as task_id,
                ef.date as date,
                ef.state as state,
                ef.company_id as company_id,
                ef.id as form_id,
                'election.form' as model,
                'election' as types,
                'Acta de Eleccion' as title
            from election_form ef
            inner join project_task pt on ef.task_id = pt.id
            )
            union all
            (
            select 
                ii.name as form,
                pt.project_id as project_id,
                ii.task_id as task_id,
                ii.date as date,
                ii.state as state,
                ii.company_id as company_id ,
                ii.id as form_id,
                'initial.investigation' as model,
                'initial' as types,
                'Investigacion Inicial' as title
            from initial_investigation ii
            inner join project_task pt on ii.task_id = pt.id
            )
            union all
            (
            select 
                ir.name as form,
                pt.project_id as project_id,
                ir.task_id as task_id,
                ir.date as date,
                ir.state as state,
                ir.company_id as company_id ,
                ir.id as form_id,
                'investigation.report' as model,
                'investigation' as types,
                'Investigacion de Accidentes' as title
            from investigation_report ir 
            inner join project_task pt on ir.task_id = pt.id
            )
            union all
            (
            select 
                of2.name as form,
                pt.project_id as project_id,
                of2.task_id as task_id,
                of2.date as date,
                of2.state as state,
                of2.company_id as company_id ,
                of2.id as form_id,
                'observation.form' as model,
                'observation' as types,
                'Formulario de Observacion' as title
            from observation_form of2 
            inner join project_task pt on of2.task_id = pt.id
            )
            union all
            (
            select 
                si.name as form,
                pt.project_id as project_id,
                si.task_id as task_id,
                si.date as date,
                si.state as state,
                si.company_id as company_id ,
                si.id as form_id,
                'security.inspection' as model,
                'security' as types,
                'Formulario de Inspeccion de Seguridad' as title
            from security_inspection si 
            inner join project_task pt on si.task_id = pt.id
            )
            union all
            (select 
                vf.name as form,
                pt.project_id as project_id,
                vf.task_id as task_id,
                vf.date as date,
                vf.state as state,
                vf.company_id as company_id ,
                vf.id as form_id,
                'visit.form' as model,
                'visit' as types,
                'Formulario de Visita' as title
            from visit_form vf
            inner join project_task pt on vf.task_id = pt.id
            )
            ) as res
            )
            """
        self.env.cr.execute(query)

    def action_view_form(self):
        for r in self:
            return {
                    'name': r.title,
                    'res_id': r.form_id,
                    'res_model': r.model,
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'create': False,
                    },
                }
