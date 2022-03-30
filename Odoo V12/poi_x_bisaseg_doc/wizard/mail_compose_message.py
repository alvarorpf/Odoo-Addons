from odoo import _, api, fields, models, SUPERUSER_ID, tools


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    send_link = fields.Boolean('Enviar Enlace', default=True)

    @api.multi
    def action_send_mail(self):
        self2 = self.with_context(send_link=self.send_link)
        return super(MailComposer, self2).action_send_mail()
