# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class DismissedProject(models.TransientModel):
    _name = 'dismissed.project'

    project_id = fields.Many2one('project.project', string='Proyecto', required=True)
    observation = fields.Char('Observación')
    dismissed = fields.Boolean('Pausar/Continuar', default=True)

    def action_dismissed(self):
        for r in self:
            if r.project_id:
                r.project_id.dismissed = True
                r.project_id._reg_log(health='dismissed', observation=r.observation)
            else:
                raise UserError('Debe seleccionar un proyecto para poner en pausa.')

    def action_continue(self):
        for r in self:
            if r.project_id:
                r.project_id.dismissed = False
                if r.project_id.deviation <= 10:
                    health = 'in_term'
                elif 10 <= r.project_id.deviation <= 20:
                    health = 'alert'
                elif r.project_id.deviation >= 20:
                    health = 'delay'
                else:
                    health = ''
                r.project_id._reg_log(health=health, observation=r.observation)
            else:
                raise UserError('Debe seleccionar el proyecto el cual desea continuar.')
