from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class SuspendRequirement(models.TransientModel):
    _name = 'suspend.requirement'
    _description = 'Suspender Requerimiento'

    request_id = fields.Many2one('request.document', 'Documento')
    comment = fields.Char('Comentario', required=True)

    def action_suspend(self):
        for r in self:
            if r.request_id:
                r.request_id.continue_state = r.request_id.state
                r.request_id.state = 'suspend'
                r.request_id.message_post(body=r.comment, message_type='notification', partner_ids=[])
            else:
                raise UserError('Debe seleccionar un requerimiento el cual desea suspender.')