# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class OpMeasureTaken(models.Model):
    _name = 'op.measure.taken'

    name = fields.Char('Nombre', required=True)
