# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, models, fields, _
import logging
from odoo.http import request

from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    web_sale = fields.Boolean("Venta por sitio web", default=False)
    sale_error = fields.Boolean("Error en registro de venta", default=False)

    @api.multi
    def reg_sale(self):
        for r in self:
            try:
                con = self.env['ws.con']
                db, pwd, uid, service = con.service_connection()
                lines = []
                partner_id = r.create_client()
                if r:
                    for l in r.order_line:
                        _logger.debug("Ingresa order line")
                        id = l.product_id.v7_id
                        if id != 0:
                            p = service.execute(db, uid, pwd, 'product.product', 'read', id, [])
                            _logger.debug("Ingresa id")
                            _logger.debug(l.product_uom_qty)
                            _logger.debug(l.product_id.list_price_second)
                            _logger.debug(partner_id)
                            _logger.debug(p['id'])
                            _logger.debug(l.product_id.v7_id)

                            if p:
                                _logger.debug("ingresa P")
                                lines.append((0, 0, {
                                    'product_id': p['id'],
                                    'product_uom_qty': l.product_uom_qty,
                                    'name': p['name'],
                                    'price_unit': l.product_id.list_price_second,
                                    'state': 'draft',
                                    'order_partner_id': partner_id,
                                    'invoiced': False,
                                    'sequence': 10,
                                    'th_weight': 0,
                                    'delay': 7,
                                    'tax_id': [[6, False, [p['taxes_id'][0]]]],
                                }))
                                _logger.debug("termina P")

                        if l.event_line_id:
                            _logger.debug("entra event line")
                            _logger.debug(l.event_line_id.ws_event_id.id)
                            _logger.debug(l.event_line_id.id)
                            _logger.debug(r.carrier_id)
                            _logger.debug(r.carrier_id.delivery_type)
                            values = {
                                'name': r.partner_id.name,
                                'street': r.partner_id.street,
                                'city': r.partner_id.city,
                                'phone': r.partner_id.phone,
                                'display_name': r.partner_id.name,
                                'ci': r.partner_id.ci,
                                'razon_invoice': r.partner_id.razon,
                                'event': l.event_line_id.ws_event_id.id,
                                'line': l.event_line_id.id,
                                'delivery_type': r.carrier_id and r.carrier_id.id or False,
                                'razon': r.partner_id.razon or '',
                                'nit': r.partner_id.nit or 0,
                            }
                            _logger.debug("sale event line")
                            event = request.env['ws.event.11'].sudo()
                            _logger.debug("event sudo")
                            reg = event.reg_purchase(values)
                    _logger.debug("Ingresa data")
                    data = {
                        'partner_id': partner_id,
                        'pricelist_id': 1,
                        'partner_invoice_id': partner_id,
                        'partner_shipping_id': partner_id,
                        'currency_id_sec': 62,
                        'order_line': lines,
                        'shop_id': 2,
                        'web_service': True,
                        'origin': 'eCommerce',
                    }
                    _logger.debug("crear venta")
                    order_id = service.execute(db, uid, pwd, 'sale.order', 'create', data)
                    # confirmed = service.execute(db, uid, pwd, 'sale.order', 'action_button_confirm', order_id, [])
                    msg_data = {
                        'body': "Esta Orden ha sido pagada desde el eCommerce. Revise los registros de la pasarela de pago para procesar esta orden",
                        'subject': "Orden confirmada y pagada",
                    }
                    notified = service.execute(db, uid, pwd, 'sale.order', 'message_post', order_id, msg_data)

                    r.web_sale = True
                    r.sale_error = False
            except:
                r.web_sale = True
                r.sale_error = True
            finally:
                 mail_template = self.env.ref('poi_x_karlovy_web.email_template_karlovy')
                 mail_template.send_mail(self.id, force_send=True)
            return True

    @api.multi
    def create_client(self):
        for r in self:
            if r. partner_id:
                partner_data = {
                    'name': r.partner_id.name,
                    'lang': 'es_BO',
                    'company_id': 1,
                    'use_parent_address': False,
                    'active': True,
                    'street': r.partner_id.street,
                    'supplier': False,
                    'city': r.partner_id.city,
                    'employee': False,
                    'type': 'contact',
                    'mobile': r.partner_id.phone,
                    'is_company': False,
                    'opt_out': False,
                    'display_name': r.partner_id.name,
                    'ci': r.partner_id.ci,
                    'razon_invoice': r.partner_id.razon,
                    'razon': r.partner_id.razon,
                    'nit': r.partner_id.nit,
                }
                con = self.env['ws.con']
                db, pwd, uid, service = con.service_connection()
                p = service.execute(db, uid, pwd, 'res.partner', 'create', partner_data)
                return p

    @api.multi
    def _cart_event_update(self, product_id=None, event_line_id=None, line_id=None, add_qty=0, set_qty=0,
                           attributes=None, **kwargs):
        """ Add or set product quantity, add_qty can be negative """
        self.ensure_one()
        SaleOrderLineSudo = self.env['sale.order.line'].sudo()

        try:
            if add_qty:
                add_qty = float(add_qty)
        except ValueError:
            add_qty = 1
        try:
            if set_qty:
                set_qty = float(set_qty)
        except ValueError:
            set_qty = 0
        quantity = 0
        order_line = False
        if self.state != 'draft':
            request.session['sale_order_id'] = None
            raise UserError(_('It is forbidden to modify a sales order which is not in draft status'))
        if line_id is not False:
            order_lines = self._cart_find_product_line(product_id, line_id, **kwargs)
            order_line = order_lines and order_lines[0]

        # Create line if no line with product_id can be located
        if not order_line:
            values = self._website_product_id_change(self.id, product_id, qty=1)
            values['name'] = self._get_line_description(self.id, product_id, attributes=attributes)
            order_line = SaleOrderLineSudo.create(values)

            try:
                order_line._compute_tax_id()
            except ValidationError as e:
                # The validation may occur in backend (eg: taxcloud) but should fail silently in frontend
                _logger.debug("ValidationError occurs during tax compute. %s" % (e))
            if add_qty:
                add_qty -= 1

        # compute new quantity
        if set_qty:
            quantity = set_qty
        elif add_qty is not None:
            quantity = order_line.product_uom_qty + (add_qty or 0)

        # Remove zero of negative lines
        if quantity <= 0:
            order_line.unlink()
        else:
            # update line
            values = self._website_product_id_change(self.id, product_id, qty=quantity)
            if self.pricelist_id.discount_policy == 'with_discount' and not self.env.context.get('fixed_price'):
                order = self.sudo().browse(self.id)
                product_context = dict(self.env.context)
                product_context.setdefault('lang', order.partner_id.lang)
                product_context.update({
                    'partner': order.partner_id.id,
                    'quantity': quantity,
                    'date': order.date_order,
                    'pricelist': order.pricelist_id.id,
                })
                product = self.env['product.product'].with_context(product_context).browse(product_id)
                values['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                    order_line._get_display_price(product),
                    order_line.product_id.taxes_id,
                    order_line.tax_id,
                    self.company_id
                )
                values['event_line_id'] = event_line_id
            order_line.write(values)

        return {'line_id': order_line.id, 'quantity': quantity}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    event_line_id = fields.Many2one('ws.event.lines.11', string='ID de linea de evento')