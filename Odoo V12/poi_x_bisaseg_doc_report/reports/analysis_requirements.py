from odoo import models, fields, api, _, tools


class AnalysisRequirements(models.Model):
    _name = 'analysis.requirements'
    _description = 'Reporte Analisis de Requerimientos'
    _auto = False

    request_id = fields.Many2one('request.document', 'Requerimiento')
    title = fields.Char('Título')
    type_id = fields.Many2one('request.doc.type', 'Tipo de Requerimiento')
    type2_id = fields.Many2one('request.doc.type2', 'Tipo')
    user_id = fields.Many2one('res.users', 'Solicitante')
    department_id = fields.Many2one('hr.department', 'Área Solicitante')
    responsible_id = fields.Many2one('res.users', 'Responsable')
    complexity_id = fields.Many2one('request.doc.complexity', 'Complejidad')
    priority_id = fields.Many2one('request.doc.priority', 'Prioridad')
    date_create = fields.Date('Fecha de Creación')
    diff_days_cr = fields.Integer('Diferencia Dias C/S')
    date_request = fields.Date('Fecha de Solicitud')
    diff_days_rm = fields.Integer('Diferencia Dias S/AG')
    date_management = fields.Date('Fecha de Aprobación Gerencia(Solicitud)')
    diff_days_ma = fields.Integer('Diferencia Dias AG/A')
    date_approved = fields.Date('Fecha de Aprobación/Priorización')
    diff_days_ac = fields.Integer('Diferencia Dias A/C')
    date_close = fields.Date('Fecha estimada de cierre')
    days_close = fields.Integer('Dias para cierre')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('request', 'Solicitado'),
        ('management', 'Aprobación Gerencia(Solicitud)'),
        ('approved', 'Aprobación/Priorización'),
        ('elaboration', 'En Elaboración'),
        ('wait_approve', 'Esperando Aprobación'),
        ('pre_published', 'Pre-Publicación'),
        ('suspend', 'Suspendido'),
        ('concluded', 'Concluido'),
        ('cancelled', 'Cancelado')], string='Estado')
    instance = fields.Char('Instancia')
    total = fields.Integer('Total')

    def _select(self):
        select_str = """
            select
                rd.id as request_id,
                rd.title as title,
                rd.type_id as type_id,
                rd.type2_id as type2_id,
                rd.user_id as user_id,
                rd.department_id as department_id,
                rd.responsible_id as responsible_id,
                rd.complexity_id as complexity_id,
                rd.priority_id as priority_id,
                rd.date_create as date_create,
                (rd.date_request - rd.date_create) as diff_days_cr,
                rd.date_request as date_request,
                (rd.date_management - rd.date_request) as diff_days_rm,
                rd.date_management as date_management,
                (rd.date_approved - rd.date_management) as diff_days_ma,
                rd.date_approved as date_approved,
                (rd.date_close - current_date) as diff_days_ac,
                rd.date_close as date_close,
                (rd.date_close - current_date) as days_close,
                rd.state as state,
                case
                    when rd.state = 'draft' then ''
                    when rd.state = 'request' then concat('Esperando Aprobacion',' ',rp.name,'-',hd.name)
                    when rd.state = 'management' then 'Esperando Aprobacion O&M'
                    when rd.state = 'approved' then 'Esperando Ejecucion O&M'
                    when rd.state = 'elaboration' then 'En Elaboracion O&M'
                    when rd.state = 'wait_approve' then (select 
                                                concat('Esperando Aprobacion:',res_p.name,'-',hrd.name)
                                                from muk_quality_docs_document as doc
                                                inner join document_auth_circuit as docac on doc.id = docac.document_id
                                                inner join res_users as res on  docac.user_id = res.id
                                                inner join res_partner as res_p on res.partner_id = res_p.id
                                                inner join hr_department as hrd on res_p.department_id = hrd.id
                                                where docac.register = False and doc.request_id = rd.id
                                                order by docac.sequence asc
                                                limit 1)
                    when rd.state = 'pre_published' then 'Esperando version Final O&M'
                    else ''
                end as instance,
                1 as total
            from request_document as rd
            inner join res_users as ru on rd.parent = ru.id
            inner join res_partner as rp on ru.partner_id = rp.id
            inner join hr_department as hd on rd.department_id = hd.id
            order by rd.id asc
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
            ) as analysis_requirements
            )""" % (self._table, self._select()))

