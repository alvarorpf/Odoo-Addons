from odoo import models, fields


class OpMediaType(models.Model):
    _inherit = 'op.media.type'
    _description = 'Tipo de Medio'

    code = fields.Char('Code', size=64, required=False)
