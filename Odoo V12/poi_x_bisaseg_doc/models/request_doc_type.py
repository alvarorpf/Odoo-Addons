from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RequestDocType(models.Model):
    _name = "request.doc.type"

    name = fields.Char('Nombre', required=True)

class RequestDocType2(models.Model):
    _name = "request.doc.type2"

    name = fields.Char('Nombre', required=True)