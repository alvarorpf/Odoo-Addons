from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DocumentAuthCircuit(models.Model):
    _name = "document.auth.circuit"
    _order = 'sequence'

    document_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    sequence = fields.Integer('Secuencia', default=1)
    user_id = fields.Many2one('res.users', string='Usuario')
    approved = fields.Boolean('Aprobado')
    refused = fields.Boolean('Rechazado')
    register = fields.Boolean('Accion de Registro')
    date = fields.Date('Fecha')
    comment = fields.Char('Comentario')

    @api.constrains('document_id', 'user_id')
    def _check_approver(self):
        for r in self:
            value = r.document_id.auth_circuit_ids.filtered(lambda x: x.user_id == r.user_id)
            if len(value)>1:
                raise ValidationError(_('No puede asignar dos veces a un mismo aprobador dentro del circuito.'))

    @api.multi
    def unlink(self):
        for r in self:
            user = self.env.user
            if user.has_group('poi_x_bisaseg_doc.group_o_and_m'):
                if r.register:
                    raise UserError(_('No se puede eliminar del circuito de aprobación a un usuario aprobador que realizó una acción.'))
                else:
                    if r.document_id.document_child_ids:
                        childs = r.document_id.document_child_ids.filtered(lambda x: x.request_id.id == r.document_id.request_id.id)
                        if childs:
                            for c in childs:
                                auth = self.env['document.auth.circuit'].search([('document_id', '=', c.id), ('user_id', '=', r.user_id.id)])
                                auth.unlink()
                    return models.Model.unlink(self)
            else:
                raise UserError(_('Usted no cuenta con el permiso para eliminar usuarios del circuito de autorización.'))


class DocumentCollaborator(models.Model):
    _name = 'document.collaborator'

    document_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    user_id = fields.Many2one('res.users', 'Colaborador', required=True)
    active = fields.Boolean('Activo')

    @api.model
    def create(self, values):
        record = super(DocumentCollaborator, self).create(values)
        record.document_id.message_subscribe([record.user_id.partner_id.id])
        body = """%s se te añadio como nuevo colaborador en %s""" % (record.user_id.name, record.document_id.name)
        record.document_id.message_post(body=body, message_type='notification', partner_ids=[record.user_id.partner_id.id])
        return record