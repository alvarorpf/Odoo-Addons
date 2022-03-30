from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentUserApproved(models.Model):
    _name = "document.user.approved"
    _order = 'sequence, id'

    template_id = fields.Many2one('document.template.circuit', string="Template Circuito de Autorización")
    sequence = fields.Integer('Secuencia', default=1)
    user_id = fields.Many2one('res.users', string="Usuario")