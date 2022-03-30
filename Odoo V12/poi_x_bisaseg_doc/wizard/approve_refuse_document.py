from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class ApproveRefuseDocument(models.TransientModel):
    _name = 'approve.refuse.document'
    _description = 'Aprobar o Rechazar Documento'

    approve = fields.Boolean('Aprobar')
    document_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    comment = fields.Char('Comentario')

    def action_continue(self):
        for r in self:
            if r.document_id:
                auths = r.document_id.auth_circuit_ids.filtered(lambda x: x.register != True)
                if not auths:
                    raise UserError('El documento ya registro acción de sus aprobadores')
                auth = auths[0]
                action = ''
                if auth.user_id.id == r.user_id.id:
                    auth.date = fields.Date.context_today(self)
                    auth.comment = r.comment
                    auth.register = True
                    if r.approve:
                        auth.approved = True
                        action = 'approve'
                        comment = 'Aprobación de %s' % (r.user_id.name)
                    else:
                        auth.refused = True
                        action = 'refuse'
                        comment = 'Rechazo de %s' % (r.user_id.name)
                    partner_ids = r.document_id.notification_partner()
                    r.document_id.message_post(body=comment, message_type='notification', partner_ids=partner_ids)
                    if len(auths) >= 2:
                        body = """Se necesita la aprobación/rechazo de :  %s""" % (auths[1].user_id.name)
                        # partner_ids = r.document_id.notification_partner()
                        # partner_ids.append(auths[1].user_id.partner_id.id)
                        r.document_id.message_post(body=body, message_type='notification',
                                            partner_ids=auths[1].user_id.partner_id.ids)
                    r.document_id.action_reg_log(comment=comment, activity=action, user=r.user_id.id)
                    if r.document_id.document_child_ids:
                        for c in r.document_id.document_child_ids:
                            auth_c = c.auth_circuit_ids.filtered(lambda x: x.user_id.id == r.user_id.id)
                            if auth_c:
                                auth_c.date = fields.Date.context_today(self)
                                auth_c.comment = r.comment
                                auth_c.register = True
                                if r.approve:
                                    auth_c.approved = True
                                    action = 'approve'
                                    comment = 'Aprobación de %s' % (r.user_id.name)
                                else:
                                    auth_c.refused = True
                                    action = 'refuse'
                                    comment = 'Rechazo de %s' % (r.user_id.name)
                                c.action_reg_log(comment=comment, activity=action, user=r.user_id.id)
            else:
                raise UserError('La acción que pretende realizar no tiene asociado un documento, contacte soporte.')
