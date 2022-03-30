from odoo import models, fields, api
import datetime


class ProjecTaskAdduserWiz(models.TransientModel):
    _name = 'project.task.adduser.wiz'
    _description = 'Añadir Usuarios a la tarea'

    task_id = fields.Many2one('project.task', 'Tarea')
    type = fields.Selection([
        ('add', 'Añadir'),
        ('remove', 'Eliminar')
    ], default='add')
    user_ids = fields.Many2many('res.users', string='Usuarios')

    user_remove_ids = fields.Many2many('res.users', string="Usuarios")

    @api.multi
    def action_process(self):
        if self.type == 'add':
            user = []
            partner_ids = []
            for u in self.user_ids:
                user.append([4, u.id])
                partner_ids.append(u.partner_id.id)
                self.task_id._reg_log(user=u, observations='Asignación de usuario')
            self.task_id.assigned_ids = user
            self.task_id.message_subscribe(partner_ids=partner_ids)
        if self.type == 'remove':
            user = []
            partner_ids = []
            for u in self.user_remove_ids:
                user.append([3, u.id])
                partner_ids.append(u.partner_id.id)
                self.task_id._reg_log(user=u, observations='Eliminación de usuario')
            self.task_id.assigned_ids = user
            self.task_id.message_unsubscribe(partner_ids=partner_ids)
      
    @api.onchange('type')
    def onchage_type(self):
        user_ids = self.task_id.assigned_ids.ids
        return {
            'domain': {'user_remove_ids': [('id', 'in', user_ids)]},
        }