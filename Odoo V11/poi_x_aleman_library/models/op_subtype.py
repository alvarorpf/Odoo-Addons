from odoo import models, fields


class OpSubtype(models.Model):
    _name = 'op.subtype'
    _description = 'Subtipo'

    name = fields.Char('Nombre', size=64, required=True)
