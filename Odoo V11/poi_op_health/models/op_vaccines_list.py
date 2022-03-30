# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class OpVaccinesList(models.Model):
    _name = 'op.vaccines.list'

    name = fields.Char('Nombre', required=True)
