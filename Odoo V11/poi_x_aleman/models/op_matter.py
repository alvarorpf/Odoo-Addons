# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpSubject(models.Model):
    _inherit = 'op.subject'

    german_name = fields.Char('Nombre en Aleman', required=True)
    type_id = fields.Many2one('op.type', 'Tipo', required=True)
    matter_type_id = fields.Many2one('op.matter.type', 'Tipo de Materia', required=True)


