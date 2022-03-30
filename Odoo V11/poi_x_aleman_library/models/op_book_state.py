from odoo import models, fields


class OpBookState(models.Model):
    _name = 'op.book.state'

    name = fields.Char('Nombre', size=64, required=True)
