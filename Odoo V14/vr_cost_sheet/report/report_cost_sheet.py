# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class ReportCostSheet(models.Model):
    _name = "report.cost.sheet"
    _auto = False
    _order = 'purchase_id asc'

    purchase_id = fields.Many2one('purchase.order', string='Orden de Compra')
    picking_id = fields.Many2one('stock.picking', string='Transferencia')
    concept = fields.Selection([('1', 'Valor FOB'), ('2', 'Costeo')], string='Concepto')
    #product_type = fields.Selection([('product', 'Producto'), ('product_purchase', 'Producto de Compra'), ('product_cost', 'Producto de Costo')], string='Tipo de Producto')
    relation = fields.Char('Relacion')
    product_id = fields.Many2one('product.product', string='Producto')
    valor = fields.Float('Total')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'report_cost_sheet')
        query = """
        CREATE OR REPLACE VIEW report_cost_sheet AS (
        select 
            row_number() over() as id,
            resultado.purchase_id as purchase_id,
            resultado.picking_id as picking_id,
            resultado.concept as concept,            
            resultado.relation as relation,
            resultado.product_id as product_id,
            resultado.value as valor
        from(
        (
        select 
            po.id purchase_id,
            sp.id picking_id,
            '1' as concept,
            'product' as product_type,
            am.name relation,
            pp.id product_id,
            case 
            	when spt.code = 'incoming' then aml.credit 
            	when spt.code = 'outgoing' then aml.credit * -1
            	else 0
            end as value
        from purchase_order po 
        inner join (	
        select distinct 
            pol.order_id, 
            sm.id as move_id
        from stock_move sm 
        inner join purchase_order_line pol on pol.id = sm.purchase_line_id 
        where purchase_line_id  is not null order by order_id
        ) as tabla on tabla.order_id = po.id
        inner join stock_move sm2 on sm2.id = tabla.move_id
        inner join product_product pp on sm2.product_id = pp.id 
        inner join product_template pt on pp.product_tmpl_id = pt.id
        inner join stock_picking sp on sm2.picking_id = sp.id
        inner join stock_picking_type spt on sp.picking_type_id = spt.id
        inner join account_move am on am.stock_move_id = sm2.id
        inner join account_move_line aml on am.id = aml.move_id 
        where aml.credit > 0 and sp.state='done')
        union all (
        select
            tabla.purchase_id,
            tabla.picking_id,
            tabla.concept,
            tabla.product_type,
            tabla.relation,
            tabla.product_id,
            sum(tabla.value)
        from(
        select distinct
            po.id purchase_id,
            sp.id picking_id,
            '2' as concept,
            'product_cost' as product_type,
            slc.name relation,
            sval.id line_id,
            slcl.product_id,
            case 
            	when spt.code = 'incoming' then sval.additional_landed_cost
            	when spt.code = 'outgoing' then sval.additional_landed_cost * -1
            	else 0
            end as value
        from purchase_order po 
        inner join (	
        select distinct 
            pol.order_id, 
            sm.id as move_id
        from stock_move sm 
        inner join purchase_order_line pol on pol.id = sm.purchase_line_id 
        where purchase_line_id  is not null order by order_id
        ) as tabla on tabla.order_id = po.id
        inner join stock_move sm2 on sm2.id = tabla.move_id
        inner join stock_picking sp on sm2.picking_id = sp.id
        inner join stock_picking_type spt on sp.picking_type_id = spt.id
        inner join stock_landed_cost_stock_picking_rel slcspr on sp.id = slcspr.stock_picking_id 
        inner join stock_landed_cost slc on slcspr.stock_landed_cost_id = slc.id
        inner join stock_valuation_adjustment_lines sval on slc.id = sval.cost_id 
        inner join stock_landed_cost_lines slcl on slcl.id = sval.cost_line_id
        where slc.state = 'done' and sp.state = 'done'
        )as tabla
        group by tabla.purchase_id, tabla.picking_id, tabla.concept, tabla.product_type, tabla.relation, tabla.product_id
        order by tabla.purchase_id, tabla.product_id
        )
        order by purchase_id
        ) as resultado
        )
        """
        self.env.cr.execute(query)