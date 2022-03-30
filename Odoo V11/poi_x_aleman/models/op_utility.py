# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime

class OpYear(models.Model):
    _name = "op.year"

    name = fields.Char('Año')

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
         'La Gestion Escolar es Unica !')
    ]

    @api.multi
    def get_last_year(self):
        date = datetime.strptime('01-01-'+self.name, '%d-%m-%Y')
        last_year = date.year -1
        year_id = self.search([('name', '=', str(last_year))])
        return year_id

    @api.multi
    def get_next_year(self):
        date = datetime.strptime('01-01-' + self.name, '%d-%m-%Y')
        last_year = date.year + 1
        year_id = self.search([('name', '=', str(last_year))])
        return year_id


class OpMonth(models.Model):
    _name = "op.month"
    _rec_name = "literal"
    _order = "sequence asc"

    name = fields.Char('Mes')
    literal = fields.Char('Descripcion')
    initials = fields.Char('Abreviacion')
    sequence = fields.Integer('Secuencia')
    active = fields.Boolean('Activo', default=False)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
         'El Periodo Escolar es Unico !')
    ]

class OpPriority(models.Model):
    _name = "op.priority"

    name = fields.Char('Mes')
