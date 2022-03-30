from odoo import api, fields, models, _
import datetime


class GeneralLedgerAleman(models.AbstractModel):
    _name = 'general.ledger.aleman'
    _auto = False

    code = fields.Char('')
    name = fields.Char('')
    company_id = fields.Many2one('res.company')
    balance_bs = fields.Float('')
    balance_usd = fields.Float('')
    balance_eur = fields.Float('')

    @api.model_cr
    def init(self):
        cr = self._cr
        self.build_view(cr=cr, context={})

    @api.model
    def build_view(self, cr, context=None):
        cr = self.env.cr
        context = context or self._context or {}
        where_part = 'where True'
        currency_adjust = ""
        if context.get('date_ini', False) and context.get('date_end', False):
            where_part = "%s and aml.date between '%s' and '%s'" % (where_part, context.get('date_ini', '0'), context.get('date_end', '0'))
            currency_adjust = " and cr.name::date <= '%s'" % context.get('date_end', '0')
        elif context.get('date_ini', False) and not context.get('date_end', False):
            where_part = "%s and aml.date>='%s'" % (where_part, context.get('date_ini', '0'))
        elif context.get('date_end', False) and not context.get('date_ini', False):
            where_part = "%s and aml.date<='%s'" % (where_part, context.get('date_end', '0'))
            currency_adjust = " and cr.name::date <= '%s'" % context.get('date_end', '0')

        charge = " " \
                 "left outer join ( " \
                 "select " \
                 "cr.name::date as date, " \
                 "cr.rate " \
                 "from res_currency_rate cr where cr.currency_id=3 %s order by name desc limit 1 " \
                 ") usd on usd.date <= current_date " \
                 " " \
                 "left outer join ( " \
                 "select " \
                 "cr.name::date as date, " \
                 "cr.rate " \
                 "from res_currency_rate cr where cr.currency_id=1 %s order by name desc limit 1 " \
                 ") eur on eur.date <= current_date " % (currency_adjust, currency_adjust)
        if context.get('adjust', False) == 'not_adjust':
            charge = " " \
                     "left outer join ( " \
                     "select " \
                     "cr.name::date as from_date, " \
                     "cr.rate, " \
                     "coalesce(((LAG(cr.name::date) over (order by cr.name::date desc))::date - interval '1' day)::date,'9999-12-31'::date) as to_date " \
                     "from res_currency_rate cr where cr.currency_id=3 order by cr.name::date desc " \
                     ") usd on aml.date between usd.from_date and usd.to_date " \
                     " " \
                     "left outer join (" \
                     "select " \
                     "cr.name::date as from_date, " \
                     "cr.rate, " \
                     "coalesce(((LAG(cr.name::date) over (order by cr.name::date desc))::date - interval '1' day)::date,'9999-12-31'::date) as to_date " \
                     "from res_currency_rate cr where cr.currency_id=1 order by cr.name::date desc " \
                     ") eur on aml.date between eur.from_date and eur.to_date "
        where_part_2 = "where base.code like '1%' or base.code like '2%' or base.code like '3%'"
        group_by = "group by base.code, base.name, base.company_id"
        order_by = "order by base.code"
        select_str = """
                    DROP VIEW IF EXISTS general_ledger_aleman;
                    CREATE OR REPLACE VIEW general_ledger_aleman as (
                    SELECT row_number() over() as id, *
                        FROM(
                            select 
                                base.code as code,
                                base.name as name,
                                base.company_id as company_id,
                                sum(base.balance_bs) as balance_bs,
                                sum(base.balance_usd) as balance_usd,
                                sum(base.balance_eur) as balance_eur
                            from(
                                select 
                                    aa.code,
                                    aa.name,
                                    aml.company_id,
                                    case 
                                        when aml.company_id = 1 and aa.balance_currency_id = 63 then (aml.debit-aml.credit) *-1
                                        when aml.company_id = 1 and aa.balance_currency_id = 3 then ((aml.debit_sec-aml.credit_sec)/usd.rate) * -1
                                        when aml.company_id = 1 and aa.balance_currency_id is null then (aml.debit-aml.credit) * -1
                                    end as balance_bs,
                                    case 
                                        when aml.company_id = 1 and aa.balance_currency_id = 63 then ((aml.debit-aml.credit)*usd.rate)* -1
                                        when aml.company_id = 1 and aa.balance_currency_id = 3 then (aml.debit_sec-aml.credit_sec)* -1
                                        when aml.company_id = 3 and aa.balance_currency_id = 1 then ((aml.debit_sec-aml.credit_sec)/eur.rate)* -1
                                        when aml.company_id = 3 and aa.balance_currency_id = 3 then (aml.debit-aml.credit)* -1
                                        when aml.company_id = 1 and aa.balance_currency_id is null then (aml.debit_sec-aml.credit_sec) * -1
                                        when aml.company_id = 3 and aa.balance_currency_id is null then (aml.debit-aml.credit)* -1
                                    end as balance_usd,
                                    case 
                                        when aml.company_id = 3 and aa.balance_currency_id = 1 then (aml.debit_sec-aml.credit_sec)* -1
                                        when aml.company_id = 3 and aa.balance_currency_id = 3 then ((aml.debit-aml.credit) * eur.rate)* -1
                                        when aml.company_id = 1 and aa.balance_currency_id = 63 then (((aml.debit-aml.credit)*usd.rate)*eur.rate)* -1
                                        when aml.company_id = 1 and aa.balance_currency_id = 3 then ((aml.debit_sec-aml.credit_sec)*eur.rate)* -1
                                        when aml.company_id = 1 and aa.balance_currency_id is null then (((aml.debit-aml.credit)*usd.rate)*eur.rate)* -1
                                        when aml.company_id = 3 and aa.balance_currency_id is null then (aml.debit_sec-aml.credit_sec) * -1
                                    end as balance_eur
                                from account_move_line as aml
                                inner join  account_account as aa on aml.account_id= aa.id
                                inner join account_move as am on aml.move_id = am.id
                                %s
                                %s and am.state='posted'
                            ) as base
                            %s
                            %s
                            %s
                    ) as asd
                    )
                 """ % (charge, where_part, where_part_2, group_by, order_by)
        cr.execute(select_str)
