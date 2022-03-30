# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class OpAllergyList(models.Model):
    _name = 'op.allergy.list'

    name = fields.Char('Nombre', required=True)
