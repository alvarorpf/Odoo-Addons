from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RequestDocJustification(models.Model):
    _name = "request.doc.justification"

    name = fields.Char('Nombre', required=True)