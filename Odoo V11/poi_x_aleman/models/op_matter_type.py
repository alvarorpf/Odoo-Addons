# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpMatterType(models.Model):
    _name = 'op.matter.type'

    name = fields.Char('Nombre', required=True)
