from odoo import api, fields, models, tools, _
import xmlrpc.client as xc


class WsEvent(models.Model):
    _name = "ws.event.11"

    name = fields.Char("Nombre de Evento")
    date_start = fields.Date("Fecha de Inicio")
    date_event = fields.Date("Fecha de Evento")
    state = fields.Selection([('inicial', 'Inicial'), ('abierto', 'Abierto'), ('cancelado', 'Cancelado'), ('cerrado', 'Cerrado')], string="Estado")
    type_event = fields.Char('Tipo de Evento')
    line_ids = fields.One2many('ws.event.lines.11', 'ws_event_id', string="Regalos")
    v7_id = fields.Integer("ID V7")

    @api.model
    def sync_events(self):
        con = self.env['ws.con']
        db, pwd, uid, service = con.service_connection()
        events = service.execute(db, uid, pwd, 'create.event', 'search', [('date_start', '>=', '2020-09-01'), ('state', '=', 'abierto')])
        event_obj = self.env["ws.event.11"]
        for e in events:
            lines = []
            event = event_obj.search([("v7_id", "=", e)])
            if not event:
                data = service.execute(db, uid, pwd, 'create.event', 'read', e, [])
                if data:
                    regalos = data['regalos_lines']
                    for r in regalos:
                        data_line = service.execute(db, uid, pwd, 'regalos.line', 'read', r, [])
                        if data_line:
                            product_id = self.env["product.product"].search([("v7_id", "=", data_line['product_id'][0])])
                            lines.append((0, 0, {'name': data_line['name'],
                                                 'product_id': product_id and product_id.id or False,
                                                 'unit_price': data_line['precio_unitario'],
                                                 'state': data_line['estado'],
                                                 'v7_id': data_line['id']}))
                    event_obj.create({
                        'name': data['name'],
                        'date_start': data['date_start'],
                        'date_event': data['date_event'],
                        'state': data['state'],
                        'type_event': data['type_id'][1],
                        'line_ids': lines,
                        'v7_id': data['id'],
                    })
                    self.env.cr.commit()
            else:
                data = service.execute(db, uid, pwd, 'create.event', 'read', e, [])
                event_obj_lines = self.env["ws.event.lines.11"]
                if data:
                    regalos = data['regalos_lines']
                    for r in regalos:
                        data_line = service.execute(db, uid, pwd, 'regalos.line', 'read', r, [])
                        if data_line:
                            product_id = self.env["product.product"].search([("v7_id", "=", data_line['product_id'][0])])
                            regalos = self.env["ws.event.lines.11"].search([("v7_id", "=", data_line['id']), ('ws_event_id', '=', event.id)])
                            if regalos:
                                for r2 in regalos:
                                    r2.name = data_line['name']
                                    r2.product_id = product_id and product_id.id or False
                                    r2.unit_price = data_line['precio_unitario']
                                    r2.state= data_line['estado']
                            else:
                                event_obj_lines.create({
                                    'name': data_line['name'],
                                    'product_id': product_id and product_id.id or False,
                                    'unit_price': data_line['precio_unitario'],
                                    'state': data_line['estado'],
                                    'v7_id': data_line['id'],
                                    'ws_event_id':event.id,
                                })
                            self.env.cr.commit()
    @api.multi
    def reg_purchase(self, values):
        if not values:
            return False
        else:
            event_v7_id = self.env['ws.event.11'].search([('id', '=', int(values['event']))])
            line_v7_id = self.env['ws.event.lines.11'].search([('id', '=', int(values['line']))])
            delivery_id = self.env['delivery.carrier'].search([('id', '=', int(values['delivery_type'])), ('type_event', '=', True)])
            if not event_v7_id and not line_v7_id and not delivery_id:
                return False
            con = self.env['ws.con']
            db, pwd, uid, service = con.service_connection()
            partner_id = self.env['ws.event.11'].create_client(values)
            user = service.execute(db, uid, pwd, 'res.users', 'read', uid, ['company_id'])
            company = service.execute(db, uid, pwd, 'res.company', 'read', user['company_id'][0], ['id', 'currency_id', 'currency_id_sec'])
            partner = service.execute(db, uid, pwd, 'res.partner', 'read', partner_id, [])
            event = service.execute(db, uid, pwd, 'create.event', 'read', event_v7_id.v7_id, [])
            line = service.execute(db, uid, pwd, 'regalos.line', 'read', line_v7_id.v7_id, [])
            inv = {
                'name': event['name'],
                'origin': event['name'],
                'razon': values['razon'],
                'account_id': partner['property_account_receivable'][0],
                'journal_id': line['event_journal'][0] or None,
                'type': 'out_invoice',
                'reference': event['name'],
                'partner_id': partner_id,
                'nit': values['nit'],
                'comment': 'Evento',
                'shop_id': event['shop_id'][0],
                'currency_id': company['currency_id_sec'][0],
                'currency_id_sec': company['currency_id'][0],
                'web_service': True,
            }
            invoice = service.execute(db, uid, pwd, 'account.invoice', 'create', inv)
            inv_line = {
                'invoice_id': invoice,
                'product_id': line_v7_id.product_id.v7_id,
                'account_id': partner['property_account_receivable'][0],
                'quantity': 1,
                'price_unit': line_v7_id.unit_price,
                'name': line_v7_id.product_id.name
            }
            invoice_line = service.execute(db, uid, pwd, 'account.invoice.line', 'create', inv_line)
            if delivery_id.type_delivery_event == 'check_in':
                pass
            elif delivery_id.type_delivery_event == 'send':
                product = service.execute(db, uid, pwd, 'product.product', 'read', line_v7_id.product_id.v7_id,
                                          ['uom_id'])
                shop = service.execute(db, uid, pwd, 'sale.shop', 'read', event['shop_id'][0], ['warehouse_id'])
                warehouse = service.execute(db, uid, pwd, 'stock.warehouse', 'read', shop['warehouse_id'][0],
                                            ['lot_reserv_id', 'lot_custodia_id'])
                location_id = warehouse['lot_reserv_id'][0]
                output_id = warehouse['lot_custodia_id'][0]
                pick = {
                    'origin': event['name'],
                    'partner_id': event['titular_id'][0],
                    'type': 'out',
                    'company_id': company['id'],
                    'move_type': 'direct',
                    'note': "",
                    'state': 'draft',
                    'invoice_state': 'none',
                    'auto_picking': True,
                }
                picking = service.execute(db, uid, pwd, 'stock.picking.out', 'create', pick)
                stock = {
                    'name': line_v7_id.product_id.name,
                    'item': 0,
                    'product_uom': product['uom_id'][0],
                    'product_uos': product['uom_id'][0],
                    'picking_id': picking,
                    'price_unit': line_v7_id.unit_price,
                    'product_id': line_v7_id.product_id.v7_id,
                    'product_uos_qty': 1,
                    'product_qty': 1,
                    'tracking_id': False,
                    'state': 'draft',
                    'location_id': location_id,
                    'location_dest_id': output_id,
                }
                move = service.execute(db, uid, pwd, 'stock.move', 'create', stock)
                service.exec_workflow(db, uid, pwd, 'stock.picking', 'button_confirm', picking)
                service.exec_workflow(db, uid, pwd, 'stock.picking', 'force_assign', picking)
                service.execute(db, uid, pwd, 'regalos.line', 'write', line_v7_id.v7_id, {'picking_id': picking})
            elif delivery_id.type_delivery_event == 'send_dir':
                product = service.execute(db, uid, pwd, 'product.product', 'read', line_v7_id.product_id.v7_id,
                                          ['uom_id'])
                shop = service.execute(db, uid, pwd, 'sale.shop', 'read', event['shop_id'][0], ['warehouse_id'])
                warehouse = service.execute(db, uid, pwd, 'stock.warehouse', 'read', shop['warehouse_id'][0],
                                            ['lot_reserv_id', 'lot_custodia_id'])
                location_id = warehouse['lot_reserv_id'][0]
                output_id = warehouse['lot_custodia_id'][0]
                pick = {
                    'origin': event['name'],
                    'partner_id': event['titular_id'][0],
                    'type': 'out',
                    'company_id': company['id'],
                    'move_type': 'direct',
                    'note': "",
                    'state': 'draft',
                    'invoice_state': 'none',
                    'auto_picking': True,
                }
                picking = service.execute(db, uid, pwd, 'stock.picking.out', 'create', pick)
                stock = {
                    'name': line_v7_id.product_id.name,
                    'item': 0,
                    'product_uom': product['uom_id'][0],
                    'product_uos': product['uom_id'][0],
                    'picking_id': picking,
                    'price_unit': line_v7_id.unit_price,
                    'product_id': line_v7_id.product_id.v7_id,
                    'product_uos_qty': 1,
                    'product_qty': 1,
                    'tracking_id': False,
                    'state': 'draft',
                    'location_id': location_id,
                    'location_dest_id': output_id,
                }
                move = service.execute(db, uid, pwd, 'stock.move', 'create', stock)
                service.exec_workflow(db, uid, pwd, 'stock.picking', 'button_confirm', picking)
                service.exec_workflow(db, uid, pwd, 'stock.picking', 'force_assign', picking)
                service.execute(db, uid, pwd, 'regalos.line', 'write', line_v7_id.v7_id, {'picking_id': picking})
                inv_line_delivery = {
                    'invoice_id': invoice,
                    'product_id': delivery_id.product_id.v7_id,
                    'account_id': partner['property_account_receivable'][0],
                    'quantity': 1,
                    'price_unit': delivery_id.product_id.list_price_second,
                    'name': delivery_id.product_id.name
                }
                invoice_line = service.execute(db, uid, pwd, 'account.invoice.line', 'create', inv_line_delivery)
            # service.exec_workflow(db, uid, pwd, 'account.invoice', 'invoice_open', invoice)
            service.execute(db, uid, pwd, 'regalos.line', 'write', line_v7_id.v7_id, {'factura': invoice, 'partner_id': partner_id, 'estado': 'vendido'})
            line_v7_id.state = 'vendido'

    @api.multi
    def create_client(self, values):
        partner_data = {
                    'name': values['name'],
                    'lang': 'es_BO',
                    'company_id': 1,
                    'use_parent_address': False,
                    'active': True,
                    'street': values['street'],
                    'supplier': False,
                    'city': values['city'],
                    'employee': False,
                    'type': 'contact',
                    'mobile': values['phone'],
                    'is_company': False,
                    'opt_out': False,
                    'display_name': values['name'],
                    'ci': values['ci'],
                    'razon_invoice': values['razon'],
                    'razon': values['razon'],
                    'nit': values['nit'],
                }
        con = self.env['ws.con']
        db, pwd, uid, service = con.service_connection()
        p = service.execute(db, uid, pwd, 'res.partner', 'create', partner_data)
        return p


class WsEventLines(models.Model):
    _name = "ws.event.lines.11"

    ws_event_id = fields.Many2one("ws.event.11", 'Evento')
    name = fields.Char("Nombre de Regalo")
    product_id = fields.Many2one("product.product", string="Producto")
    unit_price = fields.Float("Precio")
    state = fields.Selection([('libre', 'Libre'), ('vendido', 'Vendido'), ('entregado', 'Entregado'), ('entregado_', 'Entregado'),
                              ('recogido', 'Recogido'), ('pago_parcial', 'Pago parcial'), ('traspasado','Traspasado'), ('devuelto', 'Devuelto'), ('para_entrega', 'Ventas X Selección'),
                              ('anulado', 'Anulado')], string="Estado")
    v7_id = fields.Integer("ID V7")
