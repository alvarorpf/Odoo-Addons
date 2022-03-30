from odoo import models, fields, api, tools, _


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def is_download(self):
        return True
