from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentSystem(models.Model):
    _name = "document.system"

    name = fields.Char('Descripcion', required=True)
