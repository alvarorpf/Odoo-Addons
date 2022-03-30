from odoo import models, fields


class OpCduCode(models.Model):
    _name = 'op.cdu.code'

    name = fields.Char('Nombre', size=64, required=True)
