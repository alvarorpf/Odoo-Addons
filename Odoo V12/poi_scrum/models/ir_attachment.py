from odoo import models, fields, api, tools, _


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    expiration_date = fields.Date('Fecha de Vencimiento')
    project_stage_id = fields.Many2one('project.stage.base', string="Etapa de Proyecto")
    first_approval = fields.Boolean('Aprobado 1')
    second_approval = fields.Boolean('Aprobado 2')
    third_approval = fields.Boolean('Aprobado 3')
    first_approval_id = fields.Many2one('res.users', string='Aprobador 1')
    second_approval_id = fields.Many2one('res.users', string='Aprobador 2')
    third_approval_id = fields.Many2one('res.users', string='Aprobador 3')