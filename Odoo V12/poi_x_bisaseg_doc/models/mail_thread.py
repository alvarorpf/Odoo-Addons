from odoo import _, api, exceptions, fields, models, tools


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def _notify_get_groups(self, message, groups):
        groups = super()._notify_get_groups(message, groups)
        if self.env.context.get('send_link') == False:
            for group_name, group_method, group_data in groups:
                group_data['has_button_access'] = False
        return groups