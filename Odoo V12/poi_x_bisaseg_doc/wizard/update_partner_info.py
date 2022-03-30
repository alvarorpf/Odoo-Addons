from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class UpdatePartnerInfo(models.TransientModel):
    _name = 'update.partner.info'
    _description = 'Actualización de Información de Contacto'

    partner_id = fields.Many2one('res.partner', 'Contacto')
    parent = fields.Many2one('res.users', 'Responsable de Área')
    department_id = fields.Many2one('hr.department', 'Area')

    def action_update(self):
        for r in self:
            if r.partner_id:
                if r.parent:
                    r.partner_id.sudo().write({'parent': r.parent and r.parent.id or False})
                if r.department_id:
                    r.partner_id.sudo().write({'department_id': r.department_id and r.department_id.id or False})
            else:
                raise UserError('Debe seleccionar un contacto del cual se realizará la actualización de su información.')