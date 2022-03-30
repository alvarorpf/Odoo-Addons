# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta, date


class UpdateDatesWizard(models.TransientModel):
    _name = "update.dates.wizard"
    _description = 'Wizard Actualizacion de Fechas'

    date_start = fields.Date("Fecha Inicio")
    date_end = fields.Date("Fecha Fin", default=datetime.now().date())

    def action_update_dates(self):
        for r in self:
            if r.date_start and r.date_end:
                where = " and so.date_order between '%s 00:00:00'::timestamp and '%s 23:59:59'::timestamp" % (r.date_start, r.date_end)
            else:
                where = " and so.date_order <= '%s 23:59:59'::timestamp" % (r.date_end)
            query = """
                with sale_update_dates as (
                    select 
                        so.id sale_id,
                        so.name sale_name,
                        am.id invoice_id,
                        am.name invoice_name,
                        am.date invoice_date,
                        am2.id picking_move_id,
                        am2.name picking_move_name,
                        am2.date picking_move_date
                    from sale_order_line_invoice_rel solir
                    inner join sale_order_line sol on solir.order_line_id = sol.id
                    inner join account_move_line aml on aml.id = solir.invoice_line_id 
                    inner join account_move am on aml.move_id = am.id
                    inner join sale_order so on sol.order_id = so.id 
                    inner join stock_picking sp on sp.sale_id = so.id
                    inner join stock_move sm on sm.picking_id = sp.id
                    inner join account_move am2 on sm.id = am2.stock_move_id 
                    where am.state = 'posted' and am.state_sin = 'V' and am.move_type = 'out_invoice' and so.state='sale' and am.date != am2.date %s
                    order by so.name desc
                    )
                update account_move
                set date = sud.invoice_date
                from sale_update_dates sud
                where id = sud.picking_move_id;
            """ % where
            self.env.cr.execute(query)
            query2 = """
                update account_move_line aml
                set date = am.date
                from account_move am
                where am.id = aml.move_id and am.date != aml.date;
            """
            self.env.cr.execute(query2)
        return True