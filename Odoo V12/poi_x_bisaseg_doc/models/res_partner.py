from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    parent = fields.Many2one('res.users', 'Responsable de Área')