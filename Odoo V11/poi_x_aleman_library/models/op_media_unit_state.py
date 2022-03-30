from odoo import models, fields


class OpmediaUnitState(models.Model):
    _name = 'op.media.unit.state'
    _description = 'Estado Ejemplar'

    name = fields.Char('Nombre', size=64, required=True)
