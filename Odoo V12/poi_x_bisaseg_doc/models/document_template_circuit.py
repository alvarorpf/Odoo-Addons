from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentTemplateCircuit(models.Model):
    _name = "document.template.circuit"

    name = fields.Char('Nombre', required=True)
    user_approved_ids = fields.One2many('document.user.approved', 'template_id', string='Usuarios Aprobadores')