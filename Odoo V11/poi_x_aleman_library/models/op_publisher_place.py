from odoo import models, fields


class OpPublisherPlace(models.Model):
    _name = 'op.publisher.place'

    name = fields.Char('Nombre', size=64, required=True)
