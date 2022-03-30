from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime
import collections


class Document(models.Model):
    _name = "muk_quality_docs.document"
    _inherit = ["muk_quality_docs.document", "mail.thread", "mail.activity.mixin", "muk_security.mixins.access_groups"]
    _rec_name = "ref"

    state = fields.Selection(
        [('developing', 'Desarrollo'),
         ('approve', 'Aprobación'),
         ('pre_published', 'Pre Publicado'),
         ('published', 'Publicado'),
         ('suspend', 'Suspender'),
         ('cancel', 'Cancelado')],
        string='Estado', default='developing')
    partner_id = fields.Many2one("res.partner", string="Contacto Relacionado")
    type_id = fields.Many2one('document.type', string="Tipo", required=True)
    norm_id = fields.Many2one('document.norm', string="Documento Relacionado", required=True)
    auth_template_id = fields.Many2one('document.template.circuit', string="Circuito de Autorización", required=True)
    base_template_id = fields.Many2one('document.template.circuit', string="Circuito de Autorización")
    process_id = fields.Many2one('document.process', string='Proceso')
    system_id = fields.Many2one('document.system', string='Sistema')
    is_guide = fields.Boolean('Es Guía', related="type_id.is_guide")
    auth_circuit_ids = fields.One2many('document.auth.circuit', 'document_id', 'Circuito de Autorización')
    date_approved = fields.Date('Fecha de Aprobación')
    date_published = fields.Date('Fecha de Publicación')
    document_father_id = fields.Many2one('muk_quality_docs.document', 'Documento Padre')
    document_child_ids = fields.One2many('muk_quality_docs.document', 'document_father_id', string='Documentos Hijo')
    related_ids = fields.Many2many('muk_quality_docs.document',
                                   relation="document_related_rel",
                                   column1="document_id",
                                   column2="related_id",
                                   string='Documentos Relacionados')
    request_id = fields.Many2one('request.document', string='Requerimiento Origen')
    is_approved = fields.Boolean('Es Aprobador', compute='_compute_approver')
    url = fields.Char('Url de Acceso', readonly=True)
    web_page = fields.Boolean('es Una Pagina Web?', related="type_id.web_page")
    ref = fields.Char('Código de Documento', default='Nuevo', readonly=False, copy=False, store=True)
    continue_state = fields.Char('Estado por Continuar')
    version = fields.Char('Versión Actual', default='0.0.0')
    version_work = fields.Char('Versión de Trabajo', default='0.0.0')
    collaborator_ids = fields.One2many('document.collaborator', 'document_id', 'Colaboradores')
    editor = fields.Boolean('Editor de Documentos', compute='_compute_editor')
    tag_ids = fields.Many2many('document.tag', string="Etiquetas")
    is_new = fields.Boolean('Nuevo')
    area_ids = fields.Many2many('hr.department', string='Areas Relacionadas', required=True)
    mandatory_reader_ids = fields.One2many('document.mandatory.reader', 'document_id', 'Lectores Obligatorios')
    download = fields.Boolean(related='type_id.downloadable', store=True)
    last_version_date = fields.Date('Fecha ultima version')
    discharge_date = fields.Date('Fecha de baja')
    work_on_file = fields.Boolean('Se trabajo en este documento', default=False)

    @api.model
    def create(self, values):
        record = super(Document, self).create(values)
        record.action_reg_log(state=record.state, stage=record.stage_id.id, activity='create',
                              comment='Creación de Documento', user=self.env.user.id)
        followers = []
        users = []
        if record.auth_circuit_ids:
            for a in record.auth_circuit_ids:
                followers.append(a.user_id.partner_id.id)
                users.append(a.user_id.id)
        users.append(self.env.user.id)
        record.message_subscribe(followers)
        self.env['document.collaborator'].create(
            {'document_id': record.id, 'user_id': self.env.user.id, 'active': True})
        request = self.env.context.get('request', False)
        if not request:
            for a in record.area_ids:
                partner_ids = self.env['res.partner'].search([('department_id', '=', a.id)])
                if partner_ids:
                    obj = self.env['document.mandatory.reader']
                    for p in partner_ids:
                        obj.create({'document_id': record.id, 'partner_id': p.id})
        return record

    @api.multi
    def write(self, vals):
        for r in self:
            if 'stage_id' in vals:
                r.action_reg_log(stage=vals['stage_id'], comment='Cambio de Etapa', activity='stage',
                                 user=self.env.user.id)
        res = super(Document, self).write(vals)
        return res

    @api.multi
    def name_get(self):
        return [(template.id, '%s%s' % (template.name, '[%s]' % template.ref or ''))
                for template in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('ref', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    # @api.onchange('area_ids')
    # def onchange_areas(self):
    #     for r in self:
    #         if r.id:
    #             id = r.id
    #         else:
    #             id = self._origin.id
    #         if r.area_ids:
    #             for a in r.area_ids:
    #                 partner_ids = self.env['res.partner'].search([('department_id', '=', a.id)])
    #                 if partner_ids:
    #                     for p in partner_ids:
    #                         obj = self.env['document.mandatory.reader']
    #                         reader = obj.search([('document_id', '=', id), ('partner_id', '=', p.id)])
    #                         if not reader:
    #                             reader = obj.create({'document_id': id, 'partner_id': p.id})

    @api.onchange('auth_template_id')
    def onchange_template_id(self):
        for r in self:
            if r.auth_template_id:
                users = []
                if r.base_template_id and r.base_template_id.id:
                    if r.base_template_id.id != r.auth_template_id.id:
                        r.auth_circuit_ids = [(6, 0, [])]
                        for u in r.auth_template_id.user_approved_ids:
                            user = (0, 0, {'user_id': u.user_id.id})
                            users.append(user)
                        r.auth_circuit_ids = users
                else:
                    for u in r.auth_template_id.user_approved_ids:
                        user = (0, 0, {'user_id': u.user_id.id})
                        users.append(user)
                    r.auth_circuit_ids = users
                r.base_template_id = r.auth_template_id
            else:
                r.auth_circuit_ids = [(6, 0, [])]

    @api.depends("read_ids")
    def _compute_is_read(self):
        for record in self:
            record.is_read = self.env.user.id in record.sudo().read_ids.mapped("user_id.id")
            if record.is_read == True:
                history_r = self.env['document.history.read']
                hist = history_r.search([('document_id', '=', record.id), ('version', '=', record.version), ('user_id', '=', self.env.user.id)])
                if not hist:
                    history_r.create({
                        'document_id': record.id,
                        'version': record.version,
                        'user_id': self.env.user.id,
                        'date': fields.Datetime.now()
                    })

    @api.depends('auth_circuit_ids')
    def _compute_approver(self):
        for r in self:
            user_logged = self.env.user
            auth = r.auth_circuit_ids.filtered(lambda x: x.register != True)
            if auth:
                auth = auth[0]
                if user_logged.id == auth.user_id.id:
                    r.is_approved = True

    @api.depends('auth_circuit_ids', 'collaborator_ids')
    def _compute_editor(self):
        for r in self:
            user_logged = self.env.user
            auth = r.auth_circuit_ids.filtered(lambda x: x.user_id.id == user_logged.id)
            col = r.collaborator_ids.filtered(lambda x: x.user_id.id == user_logged.id and x.active == True)
            oandm = self.env.user.has_group('poi_x_bisaseg_doc.group_o_and_m')
            if auth or col or oandm:
                r.editor = True
    
    @api.multi
    def notification_partner(self):
        partner_ids = []
        group_approve_id = self.env.ref('poi_x_bisaseg_doc.group_o_and_m')
        partner_ids = group_approve_id.users.mapped('partner_id.id')
        return partner_ids

    def action_approve(self):
        for r in self:
            if not r.document_father_id:
                if len(r.auth_circuit_ids) > 0:
                    auths = r.auth_circuit_ids.filtered(lambda x: x.register != True)
                    if len(r.auth_circuit_ids) > 0:
                        if not auths:
                            raise UserError('El documento ya registro acción de sus aprobadores')
                    else:
                        raise UserError('Debe tener configurado al menos un aprobador para este documento.')
                    auth = auths[0]
                    body = """Se necesita la aprobación/rechazo de :  %s""" % (auth.user_id.name)
                    # Notification group o&m
                    # partner_ids = self.notification_partner()
                    # partner_ids.append(auth.user_id.partner_id.id)
                    r.message_subscribe(partner_ids=auth.user_id.partner_id.ids)
                    r.message_post(body=body, message_type='notification', partner_ids=auth.user_id.partner_id.ids)
                    r.state = 'approve'
                    r.action_reg_log(state='approve', comment='Cambio de Estado', activity='state', user=self.env.user.id)
                    childs = r.document_child_ids.filtered(lambda x: x.request_id.id == r.request_id.id)
                    if childs:
                        for c in childs:
                            c.state = 'approve'
                            c.action_reg_log(state='approve', comment='Cambio de Estado', activity='state',
                                             user=self.env.user.id)
                    if r.request_id:
                        if r.request_id.state != 'suspend':
                            r.request_id.state = 'wait_approve'
                        else:
                            raise UserError('El requerimiento se encuentra en estado de suspención por lo cual no puede continuar con la ejecución del documento.')
                else:
                    raise UserError('Se necesita configurar una circuito de aprobación.')
            else:
                raise UserError('No puede realizar esta operación desde un documento hijo.')

    def action_pre_published(self):
        for r in self:
            if not r.document_father_id:
                auths = len(r.auth_circuit_ids)
                actions = r.auth_circuit_ids.filtered(lambda x: x.register == True)
                if auths == len(actions):
                    for a in r.auth_circuit_ids:
                        if a.approved:
                            continue
                        else:
                            raise UserError('Un usuario aprobador rechazó de este documento.')
                    r.state = 'pre_published'
                    r.date_approved = fields.Date.context_today(self)
                    r.action_reg_log(state='pre_published', comment='Cambio de Estado', activity='state',
                                     user=self.env.user.id)
                    childs = r.document_child_ids.filtered(lambda x: x.request_id.id == r.request_id.id)
                    if childs:
                        for c in childs:
                            auths_c = len(c.auth_circuit_ids)
                            actions_c = c.auth_circuit_ids.filtered(lambda x: x.register == True)
                            if auths_c == len(actions_c):
                                c.state = 'pre_published'
                                c.date_approved = fields.Date.context_today(self)
                                c.action_reg_log(state='pre_published', comment='Cambio de Estado', activity='state',
                                                 user=self.env.user.id)
                            else:
                                raise UserError(
                                    'Falta el registro de aprobación o rechazo de uno de los usuarios aprobadores del documento hijo %s.' % (
                                            c.ref + '-' + c.name))
                    if r.request_id:
                        if r.request_id.state != 'suspend':
                            r.request_id.state = 'pre_published'
                        else:
                            raise UserError(
                                'El requerimiento se encuentra en estado de suspención por lo cual no puede continuar con la ejecución del documento.')
                else:
                    raise UserError('Falta el registro de aprobación o rechazo de uno de los usuarios aprobadores del documento padre.')
            else:
                raise UserError('No puede realizar esta operación desde un documento hijo.')

    def action_published(self):
        for r in self:
            if not r.document_father_id:
                official = self.env['document.history'].search([('document_id', '=', r.id), ('official', '=', True)])
                auths = len(r.auth_circuit_ids)
                actions = r.auth_circuit_ids.filtered(lambda x: x.register == True)
                # Validación para revisar el registro de los autorizadores en el documento
                if auths == len(actions):
                    for a in r.auth_circuit_ids:
                        if a.approved:
                            continue
                        else:
                            raise UserError('Un usuario aprobador rechazó de este documento.')
                    childs = r.document_child_ids.filtered(lambda x: x.request_id.id == r.request_id.id)
                    if childs:
                        for c in childs:
                            auths_c = len(c.auth_circuit_ids)
                            actions_c = c.auth_circuit_ids.filtered(lambda x: x.register == True)
                            if auths_c == len(actions_c):
                                continue
                            else:
                                raise UserError('Falta el registro de aprobación o rechazo de uno de los usuarios aprobadores del documento hijo %s.' % (c.ref + '-' + c.name))
                else:
                    raise UserError('Falta el registro de aprobación o rechazo de uno de los usuarios aprobadores del documento padre.')
                # Validación para revisar que el documento cuente con una versión oficial en el documento
                if r.web_page:
                    r.state = 'published'
                    r.date_published = fields.Date.context_today(self)
                    r.action_reg_log(state='published', comment='Cambio de Estado', activity='state', user=self.env.user.id)
                    childs = r.document_child_ids.filtered(lambda x: x.request_id.id == r.request_id.id)
                    if childs:
                        for c in childs:
                            official_c = self.env['document.history'].search(
                                [('document_id', '=', c.id), ('official', '=', True)])
                            if official_c:
                                c.state = 'published'
                                c.date_published = fields.Date.context_today(self)
                                c.action_reg_log(state='published', comment='Cambio de Estado', activity='state',
                                                 user=self.env.user.id)
                            else:
                                raise UserError(
                                    'El documento %s no cuenta con una versión oficial de visualización.' % (
                                            c.ref + '-' + c.name))
                            if c.web_page:
                                ver = c.version
                                v = ver.split('.')
                                v[0] = str(int(v[0]) + 1)
                                v[1] = str(0)
                                v[2] = str(0)
                                c.version = '.'.join(v)
                            else:
                                c.version = c.version_work
                            if c.work_on_file:
                                c.read_ids = [(6, 0, [])]
                                c.work_on_file = False
                else:
                    if official:
                        r.state = 'published'
                        r.date_published = fields.Date.context_today(self)
                        r.action_reg_log(state='published', comment='Cambio de Estado', activity='state', user=self.env.user.id)
                        childs = r.document_child_ids.filtered(lambda x: x.request_id.id == r.request_id.id)
                        if childs:
                            for c in childs:
                                official_c = self.env['document.history'].search(
                                    [('document_id', '=', c.id), ('official', '=', True)])
                                if official_c:
                                    c.state = 'published'
                                    c.date_published = fields.Date.context_today(self)
                                    c.action_reg_log(state='published', comment='Cambio de Estado', activity='state',
                                                     user=self.env.user.id)
                                else:
                                    raise UserError('El documento %s no cuenta con una versión oficial de visualización.' % (
                                            c.ref + '-' + c.name))
                                if c.web_page:
                                    ver = c.version
                                    v = ver.split('.')
                                    v[0] = str(int(v[0]) + 1)
                                    v[1] = str(0)
                                    v[2] = str(0)
                                    c.version = '.'.join(v)
                                else:
                                    c.version = c.version_work
                                if c.work_on_file:
                                    c.read_ids = [(6, 0, [])]
                                    c.work_on_file = False
                        if r.request_id:
                            if r.request_id != 'suspend':
                                r.request_id.state = 'concluded'
                            else:
                                raise UserError('El requerimiento se encuentra en estado de suspención por lo cual no puede continuar con la ejecución del documento.')
                        if r.is_new:
                            r.is_new = False
                        if r.work_on_file:
                            r.read_ids = [(6, 0, [])]
                            r.work_on_file = False
                    else:
                        raise UserError('El documento actual no cuenta con una versión oficial de visualización.')
                if r.web_page:
                    ver = r.version
                    v = ver.split('.')
                    v[0] = str(int(v[0]) + 1)
                    v[1] = str(0)
                    v[2] = str(0)
                    r.version = '.'.join(v)
                else:
                    r.version = r.version_work
                if r.request_id:
                    if r.request_id != 'suspend':
                        r.request_id.state = 'concluded'
                    else:
                        raise UserError('El requerimiento se encuentra en estado de suspención por lo cual no puede continuar con la ejecución del documento.')
            else:
                raise UserError('No puede realizar esta operación desde un documento hijo.')

    def action_cancel(self):
        for r in self:
            if not r.document_father_id:
                if r.state != 'cancel':
                    if r.is_new:
                        r.state = 'cancel'
                        r.action_reg_log(state='cancel', comment='Documento Cancelado', activity='state', user=self.env.user.id)
                    else:
                        r.state = 'published'
                        r.action_reg_log(state='published', comment='Desarrollo de documento cancelado', activity='state', user=self.env.user.id)
                    childs = r.document_child_ids.filtered(lambda x: x.request_id.id == r.request_id.id)
                    if childs:
                        for c in childs:
                            c.with_context(child_cancel=True).action_cancel()
                    if r.request_id:
                        r.request_id.state = 'cancelled'
            else:
                cancel = self.env.context.get('child_cancel', False)
                if cancel:
                    if r.is_new:
                        r.state = 'cancel'
                        r.action_reg_log(state='cancel', comment='Documento Cancelado', activity='state', user=self.env.user.id)
                    else:
                        r.state = 'published'
                        r.action_reg_log(state='published', comment='Desarrollo de documento cancelado', activity='state', user=self.env.user.id)
                else:
                    raise UserError('No puede realizar esta operación desde un documento hijo.')

    @api.multi
    def generate_code(self):
        code_obj = self.env['document.sequence']
        for s in self:
            domain = []
            if not s.type_id:
                raise UserError('Debe seleccionar el Tipo de Documento antes de generar el código de documento.')
            if s.type_id.is_guide and not s.system_id:
                raise UserError('Debe seleccionar el Sistema antes de generar el código de documento.')
            if not s.type_id.is_guide and not s.process_id:
                raise UserError('Debe seleccionar el Proceso antes de generar el código de documento.')
            if s.type_id.is_guide:
                domain.append(['system_id', '=', s.system_id.id])
            else:
                domain.append(['process_id', '=', s.process_id.id])
            domain.append(['type_id', '=', s.type_id.id])
            code_generate = code_obj.generate(domain)
            if not code_generate:
                raise UserError('No se encuentra la secuencia generada para los criterios de generación de código de documento.')
            self.write({'ref': code_generate})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_reg_log(self, state='', stage=False, activity='', comment='', user=False):
        for r in self:
            if not state:
                state = r.state
            if not stage:
                stage = r.stage_id.id
            log = self.env['document.log']
            log.create({
                'document_id': r.id,
                'state': state,
                'user_id': user,
                'stage_id': stage,
                'activity': activity,
                'comment': comment,
            })

    def action_view_log(self):
        return {
            'name': 'Log de Documento',
            'domain': [('document_id', '=', self.id)],
            'res_model': 'document.log',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree',
            'view_type': 'form',
            'context': {}
        }

    def action_view_history(self):
        for r in self:
            user = self.env.user
            domain = []
            domain.append(('document_id', '=', r.id))
            if user.has_group('muk_quality_docs.group_muk_quality_docs_manager'):
                pass
            elif user.has_group("muk_quality_docs.group_muk_quality_docs_author"):
                auths = r.auth_circuit_ids.filtered(lambda x: x.user_id.id == user.id)
                col = r.collaborator_ids.filtered(lambda x: x.user_id.id == user.id)
                if not (auths or col):
                    domain.append(('official', '=', True))
            elif user.has_group('muk_quality_docs.group_muk_quality_docs_user'):
                domain.append(('official', '=', True))
            return {
                'name': 'Historico de Documento',
                'domain': domain,
                'res_model': 'document.history',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'tree,form',
                'view_type': 'form',
                'context': {
                    'default_document_id': r.id,
                    'create': False,
                    'edit': False,
                    'delete': False,
                }
            }

    @api.multi
    def action_send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        # try:
        #     template_id = ir_model_data.get_object_reference('poi_x_bisaseg_doc', 'email_template_document_qms')[1]
        # except ValueError:
        #     template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        readers = []
        if self.mandatory_reader_ids:
            for mr in self.mandatory_reader_ids:
                readers.append(mr.partner_id.id)
        ctx = {
            'default_model': 'muk_quality_docs.document',
            'default_res_id': self.ids[0],
            # 'default_use_template': bool(template_id),
            # 'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True,
            'default_partner_ids': readers,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_restart_circuit(self):
        for r in self:
            if len(r.auth_circuit_ids) > 0:
                for a in r.auth_circuit_ids:
                    a.approved = False
                    a.refused = False
                    a.register = False
                    a.date = ''
                    a.comment = ''
                auths = r.auth_circuit_ids.filtered(lambda x: x.register != True)
                auth = auths[0]
                body = """Se necesita la aprobación/rechazo de :  %s""" % (auth.user_id.name)
                r.message_post(body=body, message_type='notification', partner_ids=[auth.user_id.partner_id.id])
                r.action_reg_log(comment='Reinicio de Circuito de Autorización', activity='restart',
                                 user=self.env.user.id)
                childs = r.document_child_ids.filtered(lambda x: x.request_id.id == r.request_id.id)
                if childs:
                    for c in childs:
                        for ac in c.auth_circuit_ids:
                            ac.approved = False
                            ac.refused = False
                            ac.register = False
                            ac.date = ''
                            ac.comment = ''
                        c.action_reg_log(comment='Reinicio de Circuito de Autorización', activity='restart',
                                         user=self.env.user.id)
            else:
                raise UserError('Debe tener configurado al menos un usuario aprobador para reiniciar el circuto.')

    @api.multi
    def action_view_add_area(self):
        context = dict(self.env.context or {})
        context['default_doc_id'] = self.id
        return {
            'name': _('Agregar Area'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'doc.add.area',
            'view_id': self.env.ref('poi_x_bisaseg_doc.document_add_area').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

    @api.model
    def _generate_history(self):
        docs = self.env['muk_quality_docs.document'].search([])
        if docs:
            for d in docs:
                history = self.env['document.history']
                history.create({
                    'document_id': d and d.id or False,
                    'user_id': self.env.user and self.env.user.id or False,
                    'date': fields.Date.context_today(self),
                    'version': d.version or '',
                    'official': True,

                })
            
    @api.multi
    def action_view_child(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        context['default_doc_id'] = self.id
        return {
            'name': _('Documento'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'muk_quality_docs.document',
            'view_id': self.env.ref('poi_x_bisaseg_doc.poi_document_form').id,
            'type': 'ir.actions.act_window',
            # 'context': context,
            'target': 'current',
            'res_id': self.id,
        }

    # Esta funcion fue reescrita de la funcion original sin llamar ningún super
    @api.multi
    def set_stage_to_prev(self):
        for record in self:
            
            if not record.has_right_for_prev_stage:
                msg = "You are not allowed to change to the previous workflow stage."
                _logger.exception(msg)
                raise UserError(_(msg))
            
            stage_new = record.stage_id.prev_stage_id
            
            if not stage_new:
                msg = "This is already the first stage."
                _logger.exception(msg)
                raise UserError(_(msg))

            data = {
                "stage_id": stage_new.id,
            }
            if stage_new.register_discharge_date:
                data.update({
                    'discharge_date': fields.Date.today(self),
                })
            
            record.sudo().write(data)

    # Esta funcion fue reescrita de la funcion original sin llamar ningún super
    @api.multi
    def set_stage_to_next(self):
        for record in self:
        
            if not record.has_right_for_next_stage:
                msg = "You are not allowed to change to the next workflow stage."
                _logger.exception(msg)
                raise UserError(_(msg))
            
            stage_new = record.stage_id.next_stage_id
            
            if not stage_new:
                msg = "This is already the last stage."
                _logger.exception(msg)
                raise UserError(_(msg))
                
            data = {
                "stage_id": stage_new.id,
            }
            if stage_new.register_discharge_date:
                data.update({
                    'discharge_date': fields.Date.today(self),
                })
            
            record.sudo().write(data)
