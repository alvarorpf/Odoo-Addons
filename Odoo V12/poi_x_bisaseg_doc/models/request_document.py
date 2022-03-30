# -*- encoding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RequestDocument(models.Model):
    _name = "request.document"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Requerimiento de Documentos'

    @api.depends('user_id')
    def _compute_info(self):
        for r in self:
            if r.user_id and r.user_id.partner_id:
                if r.user_id.partner_id.department_id:
                    r.department_id = r.user_id.partner_id.department_id and r.user_id.partner_id.department_id.id or False
                else:
                    raise UserError('El usuario no se encuentra asignado a un Departamento de la Compañía.')
                if r.user_id.partner_id.parent:
                    r.parent = r.user_id.partner_id.parent and r.user_id.partner_id.parent.id or False
                else:
                    raise UserError('El usuario no tiene asignado un Encargado de Departamento.')

    def _default_user_id(self):
        return self.env.user

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('request', 'Solicitado'),
        ('management', 'Aprobación Gerencia(Solicitud)'),
        ('approved', 'Aprobación/Priorización'),
        ('elaboration', 'En Elaboración'),
        ('wait_approve', 'Esperando Aprobación'),
        ('pre_published', 'Pre-Publicación'),
        ('suspend', 'Suspendido'),
        ('concluded', 'Concluido'),
        ('cancelled', 'Cancelado')], string='Estado', default='draft', track_visibility='onchange', copy=False)
    name = fields.Char('Nombre', default='Nuevo', readonly=True, store=True, copy=False)
    title = fields.Char('Título de Requerimiento', required=True)
    type_id = fields.Many2one('request.doc.type', 'Tipo de Requerimiento', required=True)
    user_id = fields.Many2one('res.users', string='Solicitante', default=_default_user_id)
    department_id = fields.Many2one('hr.department', string='Área Solicitante', compute='_compute_info', store=True)
    parent = fields.Many2one('res.users', 'Monitor', compute='_compute_info', store=True)
    justification_id = fields.Many2one('request.doc.justification', 'Justificación', required=True)
    date_create = fields.Date('Fecha de Creación', default=lambda self: fields.Date.context_today(self), copy=False)
    date_request = fields.Date('Fecha de Solicitud', copy=False)
    date_management = fields.Date('Fecha de Aprobación Gerencia(Solicitud)', copy=False)
    date_approved = fields.Date('Fecha de Aprobación/Priorización', copy=False)
    description = fields.Text('Descripción Requerimiento', required=True)
    norm_id = fields.Many2one('document.norm', string='Documento Relacionado', copy=False)
    document_ids = fields.One2many('request.documents', 'request_id', string='Documentos Hijo', copy=False)
    complexity_id = fields.Many2one('request.doc.complexity', 'Complejidad')
    priority_id = fields.Many2one('request.doc.priority', 'Prioridad')
    responsible_id = fields.Many2one('res.users', string='Responsable')
    type2_id = fields.Many2one('request.doc.type2', string='Tipo')
    comment = fields.Char('Comentarios')
    date_close = fields.Date('Fecha estimada de cierre', copy=False)
    is_approved = fields.Boolean('Es Aprobador', compute='_compute_approved')
    actual_document_ids = fields.One2many('muk_quality_docs.document', 'request_id', 'Documents', copy=False)
    continue_state = fields.Char('Estado por Continuar')

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('request.document') or '/'
        return super(RequestDocument, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.state == 'draft':
            if self.user_id.id == self.env.user.id or self.env.user.id == 1:
                res = super(RequestDocument, self).write(vals)
            else:
                raise UserError('No tiene los permisos para poder realizar la actualizción de este requerimiento')
        else:
            res = super(RequestDocument, self).write(vals)
        return res

    @api.multi
    def notification_partner(self):
        partner_ids = []
        group_approve_id = self.env.ref('poi_x_bisaseg_doc.group_o_and_m')
        partner_ids = group_approve_id.users.mapped('partner_id.id')
        return partner_ids

    def action_send(self):  
        for r in self:
            r.state = 'request'
            r.date_request = fields.Date.context_today(self)
            body = """Se necesita la aprobación/rechazo de :  %s""" % (r.parent.name)
            # partner_ids = self.notification_partner()
            # partner_ids.append(r.parent.partner_id.id)
            r.message_subscribe(partner_ids=r.parent.partner_id.ids)
            r.message_post(body=body, message_type='notification', partner_ids=r.parent.partner_id.ids)

    def action_approve(self):
        for r in self:
            user_logged = self.env.user
            if r.state == 'request':
                if r.parent:
                    if user_logged.id == r.parent.id:
                        r.state = 'management'
                        r.date_management = fields.Date.context_today(self)
                        body = """Aprobado por %s: """ % (r.parent.name)
                        partner_ids = self.notification_partner()
                        r.message_post(body=body, message_type='notification', partner_ids=partner_ids)
                        approvers = self.env['request.document.approver'].search([('enable', '=', True)])
                        if approvers:
                            for a in approvers:
                                body = """Se necesita la aprobación/rechazo de: %s""" % (a.approver_id.name)
                                # partner_ids = self.notification_partner()
                                # partner_ids.append(a.approver_id.partner_id.id)
                                r.message_post(body=body, message_type='notification', partner_ids=a.approver_id.partner_id.ids)
                        else:
                            raise UserError('Debe configurar un aprobador final activo.')
                    else:
                        raise UserError('Solo el usuario configurado puede realizar la aprobación de este requerimiento.')
                else:
                    raise UserError('El usuario no tiene asignado un Encargado de Departamento.')
            elif r.state == 'management':
                approvers = self.env['request.document.approver'].search([('enable', '=', True)])
                user_approver = approvers.filtered(lambda x: x.approver_id.id == user_logged.id)
                if user_approver:
                    r.state = 'approved'
                    r.date_approved = fields.Date.context_today(self)
                    body = """Aprobado por %s """ % (user_approver.approver_id.name)
                    partner_ids = self.notification_partner()
                    r.message_post(body=body, message_type='notification', partner_ids=partner_ids)
            
                else:
                    raise UserError('No tiene permisos para aprobar este requerimiento.')

    def action_elaboration(self):
        for r in self:
            if r.norm_id:
                documents = r.document_ids.filtered(lambda x: x.select == True)
                if documents:
                    for d in documents:
                        if d.document_id.document_father_id and d.document_id.document_father_id.id:
                            doc_father = r.document_ids.filtered(lambda x: x.select == True and x.document_id.id == d.document_id.document_father_id.id)
                            if not doc_father:
                                raise UserError('Para realizar la actualización del documento %s, debe seleccionar su documento padre para continuar.' % d.document_id.name)
                        d.document_id.request_id = r.id
                        d.document_id.state = 'developing'
                        if d.document_id.auth_circuit_ids:
                            for a in d.document_id.auth_circuit_ids:
                                a.approved = False
                                a.refused = False
                                a.register = False
                                a.date = ''
                                a.comment = ''
                        if d.document_id.document_father_id:
                            for a in d.document_id.auth_circuit_ids:
                                a.unlink()
                            for na in d.document_id.document_father_id.auth_circuit_ids:
                                self.env['document.auth.circuit'].create({'document_id': d.document_id.id, 'user_id': na.user_id.id})
                        d.document_id.action_reg_log(state=d.document_id.state, comment='Cambio de estado', activity='state', user=self.env.user.id)
                    r.state = 'elaboration'
                else:
                    raise UserError('Debe seleccionar al menos un documento que se actualizará.')
            else:
                return {
                    'name': 'Creación de Documento',
                    'res_model': 'create.document',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'context': {
                        'default_request_id': r.id,
                    },
                }

    @api.depends('state')
    def _compute_approved(self):
        for r in self:
            user_logged = self.env.user
            if r.state == 'request':
                if user_logged.id == r.parent.id:
                    r.is_approved = True
            elif r.state == 'management':
                approvers = self.env['request.document.approver'].search([('enable', '=', True)])
                user_approver = approvers.filtered(lambda x: x.approver_id.id == user_logged.id)
                if user_approver:
                    r.is_approved = True
            else:
                r.is_approved = False

    @api.onchange('norm_id')
    def onchange_type(self):
        for r in self:
            if r.norm_id:
                documents = []
                r.document_ids = [(6, 0, [])]
                docs = self.env['muk_quality_docs.document'].search([('norm_id', '=', r.norm_id.id)])
                if docs:
                    for d in docs:
                        if d.document_child_ids:
                            doc = (0, 0, {'document_id': d.id, 'is_father': True})
                        else:
                            doc = (0, 0, {'document_id': d.id})
                        documents.append(doc)
                    r.document_ids = documents
            else:
                if r.document_ids:
                    r.document_ids = [(6, 0, [])]

    @api.multi
    def action_view_documents(self):
        oandm = self.env.user.has_group('poi_x_bisaseg_doc.group_o_and_m')
        if oandm:
            create = True
        else:
            create = False
        view = {
            'name': u"Documentos",
            'view_mode': 'tree,kanban,form',
            'view_type': 'form',
            'res_model': 'muk_quality_docs.document',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': [('request_id', '=', self.id)],
            'context': {'create': create, 'delete': False},
        }
        return view

    @api.multi
    def action_cancel(self):
        for r in self:
            if r.norm_id:
                documents = r.document_ids.filtered(lambda x: x.select == True and x.is_father == True)
                if documents:
                    for d in documents:
                        if d.document_id.state != 'cancel':
                            d.document_id.action_cancel()
            else:
                documents = self.env['muk_quality_docs.document'].search([('request_id', '=', r.id), ('document_father_id', '=', False)])
                if documents:
                    for d in documents:
                        if d.state != 'cancel':
                            d.action_cancel()
            r.state = 'cancelled'

    @api.multi
    def action_refresh(self):
        for r in self:
            if r.norm_id:
                documents = r.document_ids.filtered(lambda x: x.select == True)
                documents2 = r.document_ids.filtered(lambda x: x.select == False)
                if documents:
                    for d in documents:
                        if d.document_id.document_father_id:
                            doc = r.document_ids.filtered(lambda x: x.select == True and x.document_id.id == d.document_id.document_father_id.id)
                            if not doc:
                                raise UserError('Debe seleccionar un documento padre para poder realizar la actualización de los documentos.')
                        d.document_id.request_id = r.id
                        d.document_id.state = 'developing'
                        if d.document_id.auth_circuit_ids:
                            for a in d.document_id.auth_circuit_ids:
                                a.approved = False
                                a.refused = False
                                a.register = False
                                a.date = ''
                                a.comment = ''
                        if d.document_id.document_father_id:
                            for a in d.document_id.auth_circuit_ids:
                                a.unlink()
                            for na in d.document_id.document_father_id.auth_circuit_ids:
                                self.env['document.auth.circuit'].create({'document_id': d.document_id.id, 'user_id': na.user_id.id})
                        d.document_id.action_reg_log(state=d.document_id.state, comment='Cambio de estado',
                                                     activity='state', user=self.env.user.id)
                if documents2:
                    for d in documents2:
                        d.document_id.request_id = False


class RequestDocuments(models.Model):
    _name = "request.documents"

    request_id = fields.Many2one('request.document', 'Requerimiento')
    select = fields.Boolean('Seleccionar')
    document_id = fields.Many2one('muk_quality_docs.document', string='Documento')
    stage_id = fields.Many2one(related='document_id.stage_id', string="Etapa")
    state = fields.Selection(related='document_id.state', string='Estado')
    is_father = fields.Boolean('Es Padre')
