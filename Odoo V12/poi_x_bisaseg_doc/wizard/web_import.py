from odoo import models, fields, api, _


class PoiBizagiImportWizard(models.TransientModel):
    _inherit = 'poi.bizagi.import.wizard'

    @api.multi
    def import_files(self):
        res = super(PoiBizagiImportWizard, self).import_files()
        model = res.model
        res_id = res.res_id
        if model == 'muk_quality_docs.document':
            document_id = self.env[model].search([('id', '=', res_id)])
            if document_id:
                document_id.action_reg_log(comment='Importación de Archivos', activity='import', user=self.env.user.id)
