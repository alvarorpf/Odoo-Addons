# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api


class AddLinkWizard(models.TransientModel):
    _inherit = 'project.task.link.add_wizard'

    project_id = fields.Many2one('project.project', related='task_left_id.project_id')
