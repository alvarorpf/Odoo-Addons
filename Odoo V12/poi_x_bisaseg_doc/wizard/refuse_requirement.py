from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class RefuseRequirement(models.TransientModel):
    _name = 'refuse.requirement'
    _description = 'Rechazar Requerimiento'

    request_id = fields.Many2one('request.document', 'Requerimiento')
    comment = fields.Char('Comentario', required=True)

    def action_refuse(self):
        for r in self:
            if r.request_id:
                r.request_id.state = 'cancelled'
                if r.request_id.document_ids:
                    for d in r.request_id.document_ids:
                        if d.state != 'cancel':
                            d.state = 'cancel'
                            d.action_reg_log(state='cancel', comment=r.comment, activity='state', user=self.env.user.id)
                documents = self.env['muk_quality_docs.document'].search([('request_id', '=', r.request_id.id)])
                if documents:
                    for d in documents:
                        if d.state != 'cancel':
                            d.state = 'cancel'
                            d.action_reg_log(state='cancel', comment=r.comment, activity='state', user=self.env.user.id)
                r.request_id.message_post(body=r.comment, message_type='notification', partner_ids=[])
            else:
                raise UserError('La acción que pretende realizar no tiene asociado un documento, contacte soporte.')

