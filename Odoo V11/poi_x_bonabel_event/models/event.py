# -*- coding: utf-8 -*-

import uuid

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.exceptions import Warning
from odoo.osv import expression
from odoo.tools import float_compare
from datetime import datetime


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    lot_reserv_id = fields.Many2one('stock.location', string=u'Ubicación de Reserva')
    lot_consol_id = fields.Many2one('stock.location', string=u'Ubicación de Consolidacion')
    lot_custodia_id = fields.Many2one('stock.location', string=u'Ubicación de Custodia')


class CreateEvent(models.Model):
    _name = "create.event"
    _description = "Create Event"

    @api.depends('regalos_lines.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_sub = 0.0
            for line in order.regalos_lines:
                amount_sub += line.price_total
            order.update({
                # 'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                # 'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                # 'amount_total': amount_untaxed + amount_tax,
                'amount_sub': amount_sub,
                'amount_total': amount_sub,
            })

    ############BOTON ACTUALIZAR##################
    @api.model
    def button_dummy(self):
        return True

    @api.model
    def _get_default_access_token(self):
        return str(uuid.uuid4())

    #name = fields.Char('Nombre', default='New')
    name = fields.Char(string='Name')
    img_nombre = fields.Binary('Imagen', attachment=True)
    date_start = fields.Date('Fecha Inicial', required=True, default=fields.Datetime.now)
    date_exoiration = fields.Date(string='Fecha vencimineto de reserva')
    date_event = fields.Date('Fecha Evento')
    date_customer = fields.Date('Fecha Cierre', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', string=u'Tarifa', required=True)
    partner_id = fields.Many2one('res.partner', string=u'Titular', required=True)
    organizado_id = fields.Many2one('res.partner', string=u'Organizado Por:', required=True)
    child_ids = fields.Many2many('res.partner', 'res_partner_contacts_rel2', 'contacts_id', 'partner_id',
                                 'Agregar Contactos', domain=[('customer', '!=', True), ('supplier', '!=', True)])
    order_line = fields.One2many('regalos.line', 'event_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                 auto_join=True)
    telephone = fields.Char('Telefono', size=20)
    movil = fields.Char('Movil', size=20)
    email = fields.Char('Email', size=50)
    state = fields.Selection([('inicial', 'Inicial'),
                              ('cancelado', 'Cancelado'),
                              ('abierto', 'Abierto'),
                              ('cerrado', 'Cerrado'),
                              ], default='inicial')
    regalos_lines = fields.One2many('regalos.line', 'event_id', string=u'Regalos', copy=True, auto_join=True)
    note = fields.Text(string=u'Notas')
    actualizar_func = fields.Char('actualizar', size=20)
    shop_id = fields.Many2one('stock.warehouse', string=u'Tienda')
    amount_sub = fields.Float(string=u'Sub total', store=True, readonly=True, compute='_amount_all',
                              track_visibility='onchange')
    amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_amount_all',
                                track_visibility='always')
    product_id = fields.Many2one('product.product', related='regalos_lines.product_id', string='Product')
    procurement_group_id = fields.Many2one('procurement.group', 'Grupo de Abastecimiento', copy=False)
    company_id = fields.Many2one('res.company', u'Compañia',
                                 default=lambda self: self.env['res.company']._company_default_get('create.event'))
    invoice_line = fields.Many2many('regalos.line', 'tab_invoice_lines', 'event_id', 'user_id',
                                    string=u'Items a Facturar')

    # picking_id= fields.Many2one('stock.picking', 'Confirmado')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('create.event') or '/'
        return super(CreateEvent, self).create(vals)

    @api.multi
    def action_done(self):
        return self.write({'state': 'done'})

    @api.multi
    def action_unlock(self):
        self.write({'state': 'sale'})

    @api.multi
    def confirmar_evento(self):
        for order in self:
            order.order_line._action_launch_procurement_rule()
        for line in self.regalos_lines:
            line.estado_evento = 'confirmado'
        self.state = 'abierto'
        return self.id

    @api.model
    def _generate_access_token(self):
        for event in self:
            event.access_token = self._get_default_access_token()

    #########################CERRAR EVENTO################################
    @api.model
    def _make_journal_search(self):
        journal_pool = self.env['account.journal']
        return journal_pool.search([('code', '=', self.code)])

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def traspaso(self):
        assert len(self.ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('poi_event', 'data_wizard_traspaso')[1]
        except ValueError:
            compose_form_id = False
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'traspaso.wizard',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
        }

    @api.multi
    def action_event_cancel(self):
        eventos_line_pool = self.env['create.event']
        # stock_picking_pool = self.env['stock.picking']
        # account_invoice_pool = self.env['stock.picking']
        event_campos = eventos_line_pool.browse(self._ids)
        name_event = event_campos.name
        # if event_campos.picking_id:
        #     search_picking = stock_picking_pool.search([('id', '=', event_campos.picking_id.id)])
        #     if (search_picking):
        #         raise Warning(_('Error!'),
        #                       _(
        #                           'No puede cancelar el evento "%s" contiene albaran interno creado.') % name_event)  # anuncio de que borre albaran interno
        regalos_pool = self.env['regalos.line']
        validate_regalos = regalos_pool.search([('event_id', '=', self._ids)])
        # for regalos in regalos_pool.browse(validate_regalos):
        #     if (regalos.picking_id):
        #         search_invoice = account_invoice_pool.search([('id', '=', regalos.picking_id.id)])
        #         if (search_invoice):
        #             raise Warning(_('Error!'),
        #                           _(
        #                               'No puede cancelar el evento "%s" existe una factura asociada.') % name_event)
        #     if (regalos.factura):
        #         search_invoice = stock_picking_pool.search([('id', '=', regalos.picking_id.id)])
        #         if (search_picking):
        #             raise Warning(_('Error!'),
        #                           _(
        #                               'No puede cancelar el evento "%s" exite un albaran asociado.') % name_event)
        # return self.write(self._ids, {'state': 'cancelado'})
        self.state = 'cancelado'
        return self.id

    @api.model
    def close(self, cr, uid, ids, context=None):
        create_event_pool = self.pool.get('create.event')
        event_cli = create_event_pool.browse(cr, uid, ids[0], context=context)
        for line in event_cli.regalos_lines:
            if line.estado == 'para_entrega' or line.estado == 'libre' or line.estado == 'pago_parcial' or line.estado == 'vendido':
                raise Warning(_("No se puede Realizar un Traspaso de un evento con items en estado VentasXSeleccion, Libres, Pago Parcial, o Vendido."))
        monto = event_cli.saldo_favor

        if monto < -1:
            raise Warning(_('Revise el Saldo a favor antes de Cerrar Evento'))
        date_cierre = datetime.datetime.now()
        return self.write(cr, uid, ids, {'state': 'cerrado', 'date_customer': date_cierre})

    @api.model
    def titular_id_change(self):
        context = {}
        result = {}
        valor = self.titular_id
        contacts_partner = self.env['res.partner'].browse(self.titular_id)
        tarifa_partner = contacts_partner.property_product_pricelist.id
        mail_disp = contacts_partner.email
        phone_disp = contacts_partner.phone
        movil_disp = contacts_partner.mobile
        parent_disp = contacts_partner.parent_id.id
        obj_event = self.browse(self.ids)
        sql = """select id, name, phone, email 
              from res_partner 
              where parent_id= """ + str(self.titular_id) + """
              group by id, name, phone, email"""
        self.env.cr.execute(sql)
        contacts_lines = []
        ret_value = {}
        r = []
        for record in sql.fetchall():
            contacts_lines.append(record[0])
        result.update({'pricelist_id': tarifa_partner, 'telephone': phone_disp, 'email': mail_disp, 'movil': movil_disp,
                       'child_ids': contacts_lines})
        return {'value': result}


class TipoEvent(models.Model):
    _name = "tipo.event"
    _description = "Tipo de Evento"

    name = fields.Char('Tipo', size=60, required=True, help="Tipo de Evento")


class RegalosLine(models.Model):
    _name = "regalos.line"
    _description = "Lista de Regalos"

    @api.multi
    def write(self, values):
        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            self.filtered(
                lambda r: r.state == 'sale' and float_compare(r.product_uom_qty, values['product_uom_qty'],
                                                              precision_digits=precision) != 0)._update_line_quantity(
                values)
        protected_fields = self._get_protected_fields()
        if 'done' in self.mapped('event_id.state') and any(f in values.keys() for f in protected_fields):
            protected_fields_modified = list(set(protected_fields) & set(values.keys()))
            fields = self.env['ir.model.fields'].search([
                ('name', 'in', protected_fields_modified), ('model', '=', self._name)
            ])
            raise UserError(
                _('It is forbidden to modify the following fields in a locked order:\n%s')
                % '\n'.join(fields.mapped('field_description'))
            )
        result = super(RegalosLine, self).write(values)
        return result

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        taxes = 0.0
        for line in self:
            # price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes += line.product_uom_qty * line.price_unit
        line.update({
            # 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            # 'price_total': taxes['total_included'],
            'price_total': taxes,
        })

    partner_id = fields.Many2one('res.partner', string=u'Cliente')
    event_id = fields.Many2one('create.event', string=u'id ev')
    product_id = fields.Many2one('product.product', string=u'Producto', change_default=True, ondelete='restrict',
                                 required=True)
    name = fields.Text(string=u'Descripción', size=256)
    price_unit = fields.Float('Precio Unitario', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    product_uom_qty = fields.Float(string=u'Ctdad pedida', digits=dp.get_precision('Product Unit of Measure'),
                                   required=True, default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    price_total = fields.Float(compute='_compute_amount', string='Total', readonly=True, store=True)
    event_journal = fields.Many2one('account.journal', 'Metodo de pago')
    estado = fields.Selection([('libre', 'Libre'),
                               ('vendido', 'Vendido'),
                               ('entregado', 'Entregado'),
                               ('recogido', 'Recogido'),
                               ('traspasado', 'Traspasado'),
                               ('devuelto', 'Devuelto'),
                               ('anulado', 'Anulado'),
                               ], string="Estado", required=True, default="libre")
    comentarios = fields.Char('Comentarios', size=200)
    item = fields.Integer('N° item')
    estado_evento = fields.Char('Estado Evento', size=200)
    vps = fields.Char('vps', size=200)
    n_paquete = fields.Char('N. Paquete', size=50)
    consigna = fields.Char('consigna', size=50)
    sequence = fields.Integer(string='Sequence', default=10)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    price_total = fields.Float(compute='_compute_amount', string='Total', readonly=True, store=True)
    factura = fields.Many2one('account.invoice', 'Factura', readonly=True)
    invoice_line = fields.Many2many('regalos.line', 'tab_invoice_lines', 'event_id', 'user_id',
                                    string=u'Items a Facturar')

    # move_ids = fields.One2many('stock.move', 'regalos_line_id', string='Stock Moves')

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}
        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0
        product = self.product_id.with_context(
            partner=self.event_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.event_id.date_start,
            pricelist=self.event_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        result = {'domain': domain}
        title = False
        message = False
        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name
        if self.event_id.pricelist_id and self.event_id.partner_id:
            vals['price_unit'] = self._get_display_price(product)
        self.update(vals)
        return result

    @api.multi
    def _get_display_price(self, product):
        if self.event_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.event_id.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.event_id.partner_id.id, date=self.event_id.date_order,
                               uom=self.product_uom.id)
        final_price, rule_id = self.event_id.pricelist_id.with_context(product_context).get_product_price_rule(
            self.product_id, self.product_uom_qty or 1.0, self.event_id.partner_id)
        base_price, currency_id = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                              self.product_uom_qty,
                                                                                              self.product_uom,
                                                                                              self.event_id.pricelist_id.id)
        if currency_id != self.event_id.pricelist_id.currency_id.id:
            base_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(base_price,
                                                                                                            self.event_id.pricelist_id.currency_id)
        return max(base_price, final_price)

    @api.multi
    def name_get(self):
        result = []
        for so_line in self:
            name = '%s - %s' % (so_line.event_id.name, so_line.name.split('\n')[0] or so_line.product_id.name)
            if so_line.order_partner_id.ref:
                name = '%s (%s)' % (name, so_line.order_partner_id.ref)
            result.append((so_line.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            args = expression.AND([
                args or [],
                ['|', ('event_id.name', operator, name), ('name', operator, name)]
            ])
        return super(RegalosLine, self).name_search(name, args, operator, limit)

    #############CALCULAR SUB TOTAL##############
    @api.model
    # def cantidad_id_change(self, cr, uid, ids, product_id, cantidad, precio_unitario, context=None):
    def cantidad_id_change(self):
        res = {}
        sub_total = float(self.product_uom_qty) * float(self.price_unit)
        res.update({'sub_total': sub_total})
        return {'value': res}

    ######################VALIDAR ONCHANGE PRECIO UNITARIO#############################
    ##################VALIDAR EL ONCHANGE DEL ESTADO###################################
    @api.model
    # def onchange_preciounitario(self, cr, uid, ids, regalos_lines, precio_unitario):
    def onchange_preciounitario(self):
        if not self.id:
            return {}
        price_unit_selec = self.browse(self.id)[0].price_unit
        return {'value': {'price_unit': price_unit_selec}}

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(
                        product, qty, self.order_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
            if pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = product_currency or (
                product.company_id and product.company_id.currency_id) or self.env.user.company_id.currency_id
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id)

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id.id

    def _get_protected_fields(self):
        return [
            'product_id', 'name', 'price_unit', 'product_uom', 'product_uom_qty'
        ]

    @api.multi
    def _action_launch_procurement_rule(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if not line.product_id.type in ('consu', 'product'):
                continue
            qty = 0.0
            # for move in line.move_ids.filtered(lambda r: r.state != 'cancel'):
            #    qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom,
            #                                              rounding_method='HALF-UP')
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue
            group_id = line.event_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.event_id.name,
                    # 'move_type': line.order_id.picking_policy,
                    'event_id': line.event_id.id,
                    'partner_id': line.event_id.partner_id.id,
                })
                line.event_id.procurement_group_id = group_id
            else:
                updated_vals = {}
                if group_id.partner_id != line.event_id.partner_id:
                    updated_vals.update({'partner_id': line.event_id.partner_shipping_id.id})
                if updated_vals:
                    group_id.write(updated_vals)
            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty
            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom
            if not line.event_id.shop_id:
                raise Warning(_('Antes de confirmar un Evento debe asignar la Tienda de la cual se hará la reserva de inventario.'))
            try:
                self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom,
                                                  line.event_id.partner_id.property_stock_customer, line.name,
                                                  line.event_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = {}
        self.ensure_one()
        # date_planned = datetime.strptime(self.event_id.date_event + ' 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        values.update({
            'company_id': self.event_id.company_id,
            'group_id': group_id,
            # 'regalos_line_id': self.id,
            # 'date_planned': date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            # 'route_ids': self.route_id,
            'warehouse_id': self.event_id.shop_id or False,
            'partner_dest_id': self.event_id.partner_id
        })
        return values
