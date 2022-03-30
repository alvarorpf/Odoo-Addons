from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RequestDocPriority(models.Model):
    _name = "request.doc.priority"

    name = fields.Char('Nombre', required=True)