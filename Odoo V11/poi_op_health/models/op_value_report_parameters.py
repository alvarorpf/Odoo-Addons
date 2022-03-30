# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class OpValueReportParameters(models.Model):
    _name = 'op.value.report.parameters'

    name = fields.Char('Nombre', required=True)
    parameter_id = fields.Many2one('op.report.parameters', 'Parametro')
