# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpType(models.Model):
    _name = 'op.type'

    name = fields.Char('Nombre', required=True)
