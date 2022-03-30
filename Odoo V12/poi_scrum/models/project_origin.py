# coding=utf-8
from odoo import models, fields, api, tools, _


class ProjectOrigin(models.Model):
    _name = 'project.origin'

    name = fields.Char('Nombre')
