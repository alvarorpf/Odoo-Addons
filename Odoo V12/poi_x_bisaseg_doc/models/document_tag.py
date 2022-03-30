from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentTag(models.Model):
    _name = "document.tag"

    name = fields.Char('Nombre', required=True)