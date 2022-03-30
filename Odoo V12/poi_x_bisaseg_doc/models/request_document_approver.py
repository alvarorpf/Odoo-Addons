from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class RequestDocumentApprover(models.Model):
    _name = 'request.document.approver'
    _rec_name = 'approver_id'

    approver_id = fields.Many2one('res.users', string='Aprobador')
    enable = fields.Boolean('Activo')
