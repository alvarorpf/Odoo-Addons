from odoo import models, fields


class OpPublisher(models.Model):
    _inherit = 'op.publisher'

    name = fields.Char('Nombre', size=300, required=True)