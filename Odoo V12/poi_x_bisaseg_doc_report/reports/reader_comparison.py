from odoo import models, fields, api, _, tools


class ReaderComparison(models.Model):
    _name = 'reader.comparison'
    _description = 'Reporte de Comparación de Lectores'
    _auto = False

    document_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    norm_id = fields.Many2one(related='document_id.norm_id', string='Documento Relacionado')
    version = fields.Char('Versión')
    user_id = fields.Many2one('res.users', 'Lector')
    is_read = fields.Boolean('Realizó Lectura')
    read_date = fields.Datetime('Fecha de Lectura')
    is_mandatory = fields.Boolean('Es lector obligatorio?')

    def _select(self):
        select_str = """
        (select 
            dmr.document_id as document_id,
            doc.version as version,
            resu.id as user_id,
            case
                when (  select count(*) 
                        from muk_quality_docs_read mqdr 
                        where mqdr.document_id = dmr.document_id and mqdr.user_id = resu.id) = 1 then True
                else False
            end as is_read,
            (   select create_date 
                from muk_quality_docs_read mqdr 
                where mqdr.document_id = dmr.document_id and mqdr.user_id = resu.id
            ) as read_date,
            True as is_mandatory
        from document_mandatory_reader as dmr
        inner join res_users as resu on dmr.partner_id = resu.partner_id
        inner join muk_quality_docs_document as doc on dmr.document_id = doc.id
        where dmr.document_id is not null
        )
        UNION ALL
        (select 
            mqdr.document_id document_id,
            doc.version as version,
            mqdr.user_id as user_id,
            True as is_read,
            mqdr.create_date as read_date,
            False as is_mandatory
        from muk_quality_docs_read as mqdr
        inner join muk_quality_docs_document as doc on doc.id = mqdr.document_id 
        where mqdr.user_id not in ( select resu.id 
                                    from document_mandatory_reader as dmr 
                                    inner join res_users as resu on resu.partner_id = dmr.partner_id 
                                    where dmr.document_id = mqdr.document_id)
                and mqdr.document_id is not null
        )
        UNION ALL
        (	
            select
                dhr.document_id as document_id,
                dhr.version as version,
                dhr.user_id as user_id,
                True as is_read,
                dhr.date as read_date,
                False as is_mandatory
            from document_history_read as dhr
            inner join muk_quality_docs_document as doc on dhr.document_id = doc.id
            where doc.state = 'published' and doc.version != dhr.version
        )
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
            ) as reader_comparison
            )""" % (self._table, self._select()))
