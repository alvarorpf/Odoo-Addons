# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpStateCase(models.Model):
    _name = 'op.student.case'

    name = fields.Char('Nombre', required=True)
    apply_active = fields.Boolean('Aplica Activo')
    color = fields.Integer('Color')
    apply_charge = fields.Boolean('Aplica para Creacion de Cargos')

    @api.multi
    def get_case(self, name):
        case_id = False
        if name:
            case_id = self.search([('name', '=', name)])
        return case_id
