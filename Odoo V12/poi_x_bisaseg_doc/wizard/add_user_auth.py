from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class AddUserAuth(models.TransientModel):
    _name = 'add.user.auth'
    _description = 'Añadir Usuario Autorizador'

    document_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    user_id = fields.Many2one('res.users', string='Usuario', required=True)

    def action_continue(self):
        for r in self:
            if r.document_id:
                if r.user_id:
                    auth = self.env['document.auth.circuit'].create({'document_id': r.document_id.id, 'user_id': r.user_id.id})
                    r.document_id.message_subscribe([r.user_id.partner_id.id])
                    if r.document_id.document_father_id:
                        raise UserError('Solo se puede añadir autorizadores desde un documento padre.')
                    if r.document_id.document_child_ids:
                        childs = r.document_id.document_child_ids.filtered(lambda x: x.request_id.id == r.document_id.request_id.id)
                        if childs:
                            for c in childs:
                                auth_c = self.env['document.auth.circuit'].create({'document_id': c.id, 'user_id': r.user_id.id})
                else:
                    raise UserError('Debe seleccionar el usuario que se añadira al circuito de autorización.')
            else:
                raise UserError('La acción que pretende realizar no tiene asociado un documento, contacte soporte.')
