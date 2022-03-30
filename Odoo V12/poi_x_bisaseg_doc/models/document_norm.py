from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentNorm(models.Model):
    _name = "document.norm"

    name = fields.Char('Nombre', required=True)