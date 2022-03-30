# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import dateutil.parser


class PendingApprove(models.Model):
    _name = "pending.approve"
    _auto = False

    request_id = fields.Many2one('request.document', 'Requerimiento')
    document_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    user_id = fields.Many2one('res.users', 'Usuario')
    action = fields.Char('Acción')

    def _select(self):
        select_str = """
            (select 
                id as request_id,
                cast(null as integer) as document_id,
                parent as user_id,
                'Se Necesita Aprobacion de Requerimiento' as action
            from request_document 
            where state = 'request')
            UNION ALL
            (select 
                rd.id as request_id,
                cast(null as integer) as document_id,
                rda.approver_id as user_id,
                'Se Necesita Aprobacion de Requerimiento' as action
            from request_document as rd
            inner join request_document_approver as rda on rd.parent = rda.approver_id
            where rd.state = 'management' and rda.enable = true)
            UNION ALL
            (select 
                rd.id as request_id,
                cast(null as integer) as document_id,
                rda.approver_id as user_id,
                'Se Necesita Aprobacion de Requerimiento' as action
            from request_document as rd
            inner join request_document_approver as rda on rd.parent != rda.approver_id
            where rd.state = 'management' and rda.enable = true)
            UNION ALL
            (select 
                cast(null as integer) as request_id,
                doca.document_id as document_id,
                doca.user_id as user_id,
                'Se Necesita Aprobacion de Documento' as action
            from document_auth_circuit doca 
            where doca.id in 
                (   select doca2.id
                    from document_auth_circuit as doca2
                    inner join muk_quality_docs_document as doc on doc.id = doca2.document_id
                    where doca.document_id = doca2.document_id and doc.state = 'approve' and  doca2.register = false and doca2.document_id is not null and doc.document_father_id is null
                    order by doca2.sequence
                    limit 1 
                )
            )
        """
        return select_str

    @api.model_cr
    def init(self):
        table = "genera_schedule"
        self.env.cr.execute("""
                DROP VIEW IF EXISTS pending_approve;
                CREATE OR REPLACE VIEW pending_approve as (
                SELECT row_number() over() as id, *
                    FROM(
                    %s 
                    ) as asd
                )""" % self._select())

    def view_approve(self):
        for r in self:
            if r.request_id and r.request_id.id:
                return {
                    'name': 'Requerimiento',
                    'res_model': 'request.document',
                    'res_id': r.request_id.id,
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'view_mode': 'form',
                    'view_type': 'form',
                }
            elif r.document_id and r.document_id.id:
                return {
                    'name': 'Documento',
                    'res_model': 'muk_quality_docs.document',
                    'res_id': r.document_id.id,
                    'type': 'ir.actions.act_window',
                    'view_id': False,
                    'view_mode': 'form',
                    'view_type': 'form',
                }