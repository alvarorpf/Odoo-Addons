# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning


class ServiceHistory(models.Model):
    _name = "service.history"

    name = fields.Datetime("Fecha", default=fields.Datetime.now())
    charge_ids = fields.Many2many('account.charge', string="Cargos")
    state = fields.Selection([
        ('send', 'Enviado'),
        ('done', 'Realizado'),
        ('unused', 'Sin Usar'),
    ], string="Estado", default="send")
    active = fields.Boolean('Activo', default=True)
