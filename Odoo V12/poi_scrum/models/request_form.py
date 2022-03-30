# -*- encoding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RequestFormBenefit(models.Model):
    _name = 'request.form.benefit'

    name = fields.Text('Descripción')


class RequestFormOrigin(models.Model):
    _name = 'request.form.origin'

    name = fields.Char('Origen')
    description = fields.Char('Descripción')


class RequestFormBenefits(models.Model):
    _name = 'request.form.benefits'

    request_id = fields.Many2one('request.form', string='Formulario de Requerimiento')
    benefit_id = fields.Many2one('request.form.benefit', string='Descripción')
    select = fields.Boolean('Seleccionar')


class RequestFormType(models.Model):
    _name = 'request.form.type'

    request_id = fields.Many2one('request.form', string='Formulario de Requerimiento')
    origin_id = fields.Many2one('request.form.origin', string='Origen')
    description = fields.Char(string='Descripción')
    classification = fields.Boolean('Clasificación')


class RequestForm(models.Model):
    _name = "request.form"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Formulario de Requerimiento'

    state = fields.Selection([('draft', 'Borrador'), ('send', 'Enviado'), ('project', 'Proyecto')], default='draft', track_visibility='onchange', string='Estado')
    title = fields.Char('Titulo', required=True)
    name = fields.Char('Número de Solicitud', readonly=True)
    date = fields.Date('Fecha', default=lambda self: fields.Date.context_today(self), readonly=True)
    area_id = fields.Many2one('hr.department', string='Área', default=lambda self: self.env.user.department_id and self.env.user.department_id.id)
    applicant_id = fields.Many2one('res.users', string='Usuario Solicitante', default=lambda self: self.env.user)
    priority_id = fields.Many2one('project.priority', string='Prioridad')
    description = fields.Text('Descripción')
    specific_description = fields.Html('Descripción Específica', required=True)
    objective = fields.Text('Objetivo', required=True)
    normative = fields.Text('Normativa')
    affected_system = fields.Text('Sistema Afectado')
    is_problem = fields.Boolean('Es Problema')
    other_area_ids = fields.Many2many('hr.department',
                                      'request_other_area_rel',
                                      'request_id',
                                      'other_area_id',
                                      string='Otras áreas involucradas')
    benefit_ids = fields.One2many('request.form.benefits', 'request_id', string='Tipos de Requerimiento')
    type_ids = fields.One2many('request.form.type', 'request_id', string='Tipos de Requerimiento')
    process = fields.Html('Proceso')
    project_id = fields.Many2one('project.project', string='Proyecto')
    sponsor_ids = fields.Many2many('project.sponsor', string='Sponsor')
    owner_id = fields.Many2one('hr.department', string='Dueño del Proyecto', required=True)
    workflow_id = fields.Many2one(comodel_name='project.workflow', string='Workflow', default=lambda self: self.env['project.workflow'].search([])[0],)
    type_id = fields.Many2one(comodel_name="project.type", string="Tipo de Proyecto")

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('request.form') or '/'
        count = 0
        for b in values['benefit_ids']:
            if b[2]['select']:
                count = 1
        if count == 0:
            raise UserError('Debe marcar al menos uno de las opciones en la pestaña beneficios para guardar este formulario.')
        record = super(RequestForm, self).create(values)
        return record

    @api.multi
    def write(self, vals):
        res = super(RequestForm, self).write(vals)
        count = 0
        for b in self.benefit_ids:
            if b.select:
                count = 1
        if count == 0:
            raise UserError('Debe marcar al menos uno de las opciones en la pestaña beneficios para guardar este formulario.')
        return res

    @api.onchange('type_id')
    def onchange_type(self):
        for r in self:
            if r.type_id:
                r.workflow_id = r.type_id.workflow_id.id

    @api.model
    def default_get(self, fields_list):
        defaults = super(RequestForm, self).default_get(fields_list)
        benefits = self.env['request.form.benefit'].search([], order='id asc')
        origins = self.env['request.form.origin'].search([], order='id asc')
        benefit_ids = []
        origin_ids = []
        if benefits:
            for b in benefits:
                benefit_ids.append((0, 0, {'benefit_id': b.id}))
            defaults['benefit_ids'] = benefit_ids
        if origins:
            for o in origins:
                origin_ids.append((0, 0, {'origin_id': o.id, 'description': o.description}))
            defaults['type_ids'] = origin_ids
        return defaults

    def action_send(self):
        for r in self:
            r.state = 'send'

    def action_draft(self):
        for r in self:
            r.state = 'draft'

    def action_project(self):
        for r in self:
            return {
                'name': 'Proyecto',
                'res_model': 'request.form',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('poi_scrum.request_form_view_simplified').ids,
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': r.id,
                'target': 'new',
                'context': {
                    'active_ids': [r.id],
                    'active_id': r.id
                },
            }

    def action_create_project(self):
        for r in self:
            project = self.env['project.project']
            project_id = project.create({
                'name': r.title,
                'requesting_user_id': r.applicant_id and r.applicant_id.id or False,
                'owner_id': r.owner_id and r.owner_id.id or False,
                'type_id': r.type_id and r.type_id.id or False,
            })
            if project_id:
                project_id.key = r.name
                project_id.description = r.description
                project_id.workflow_id = r.workflow_id.id
                project_id.area_id = r.area_id and r.area_id.id or False
                project_id.sponsor_ids = r.sponsor_ids
                project_id.request_id = r and r.id or False
                project_id.onchange_workflow_id()
                r.write({'state': 'project', 'project_id': project_id.id})

    def action_view_project(self):
        return {
            'name': 'Proyecto',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
        }
