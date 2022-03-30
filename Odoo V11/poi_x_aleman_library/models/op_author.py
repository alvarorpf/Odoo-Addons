from odoo import models, fields


class OpAuthor(models.Model):
    _inherit = 'op.author'

    name = fields.Char('Nombre', size=300, required=True)