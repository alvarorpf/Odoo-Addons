# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning


class OpScholarship(models.Model):
    _name = "op.scholarship"

    name = fields.Char("Nombre")
    discount = fields.Float("Descuento")
    discount_total = fields.Float('Descuento Total')

    apply_first = fields.Boolean("Aplica Primera Pension")
    apply_regular = fields.Boolean("Aplica Pesion Regular")
    active_scholarship = fields.Boolean("Activo")

    is_regular = fields.Boolean("Es Regular")
    is_scholarship = fields.Boolean("Es Becado")
    is_child_local = fields.Boolean("Es hijo de Funcionario Local")
    is_child_foreign = fields.Boolean("Es hijo de Funcionario Extranjero")