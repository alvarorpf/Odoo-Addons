# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class OpDiseasesList(models.Model):
    _name = 'op.diseases.list'

    name = fields.Char('Nombre', required=True)
