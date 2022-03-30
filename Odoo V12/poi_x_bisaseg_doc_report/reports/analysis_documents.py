from odoo import models, fields, api, _, tools


class AnalysisDocuments(models.Model):
    _name = 'analysis.documents'
    _description = 'Reporte Analisis de Documentos'
    _auto = False

    ref = fields.Char('Código')
    name = fields.Char('Nombre')
    type_id = fields.Many2one('document.type', 'Tipo')
    process_id = fields.Many2one('document.process', 'Proceso')
    state = fields.Selection(
        [('developing', 'Desarrollo'),
         ('approve', 'Aprobación'),
         ('pre_published', 'Pre Publicado'),
         ('published', 'Publicado'),
         ('suspend', 'Suspender'),
         ('cancel', 'Cancelado')], string='Estado')
    norm_id = fields.Many2one('document.norm', 'Norma')
    date_approved = fields.Date('Fecha de Aprobación')
    date_published = fields.Date('Fecha de Publicación')
    partner_id = fields.Many2one('res.partner', 'Empresa Relacionada')
    total = fields.Integer('Total')
    total_read = fields.Integer('Total Leidos')

    def _select(self):
        select_str = """
        select 
            doc.ref,
            doc.name,
            doc.type_id,
            doc.process_id,
            doc.state,
            doc.norm_id,
            doc.date_approved,
            doc.date_published,
            doc.partner_id,
            1 as total,
            (select count(*) from muk_quality_docs_read as docr where docr.document_id = doc.id) as total_read
        from muk_quality_docs_document as doc
            
        """
        return select_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT row_number() over() as id, *
            from
            (
                %s
            ) as analysis_documents
            )""" % (self._table, self._select()))
