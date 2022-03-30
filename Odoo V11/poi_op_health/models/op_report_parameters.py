# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class OpReportParameters(models.Model):
    _name = 'op.report.parameters'

    name = fields.Char('Nombre', required=True)
