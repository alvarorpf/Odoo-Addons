# coding=utf-8
from odoo import models, fields, api, tools, _


class ProjectStageBase(models.Model):
    _name = 'project.stage.base'
    _order = 'sequence asc'

    name = fields.Char('Nombre')
    sequence = fields.Integer('Secuencia')
    is_dev = fields.Boolean('Es Desarrollo')
    end_stage = fields.Boolean('Etapa Final')
