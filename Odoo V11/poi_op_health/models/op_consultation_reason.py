# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from dateutil import parser


class OpConsultationReason(models.Model):
    _name = 'op.consultation.reason'

    name = fields.Char('Nombre', required=True)
