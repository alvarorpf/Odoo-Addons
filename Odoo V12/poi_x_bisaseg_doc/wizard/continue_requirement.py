from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class ContinueRequirement(models.TransientModel):
    _name = 'continue.requirement'
    _description = 'Continuar Requerimiento'

    request_id = fields.Many2one('request.document', 'Documento')
    comment = fields.Char('Comentario', required=True)

    def action_continue(self):
        for r in self:
            if r.request_id:
                r.request_id.state = r.request_id.continue_state
                r.request_id.continue_state = ''
                r.request_id.message_post(body=r.comment, message_type='notification', partner_ids=[])
            else:
                raise UserError('Debe seleccionar un requerimiento el cual desea suspender.')