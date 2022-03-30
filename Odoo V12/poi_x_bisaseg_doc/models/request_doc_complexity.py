from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RequestDocComplexity(models.Model):
    _name = "request.doc.complexity"

    name = fields.Char('Nombre')