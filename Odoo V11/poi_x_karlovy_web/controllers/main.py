from odoo import http

from addons.website_sale.controllers.main import WebsiteSale
from werkzeug.exceptions import Forbidden, NotFound

import logging
from odoo import api, models, fields, _
from odoo.http import request

from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CustomWebsiteSale(WebsiteSale):

    @http.route(['/shop/payment/transaction/',
                 '/shop/payment/transaction/<int:so_id>',
                 '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public",
                website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        res = super(CustomWebsiteSale, self).payment_transaction(acquirer_id, save_token=False, so_id=None,
                                                                 access_token=None, token=None, **kwargs)
        # La OV se debería registrar DEPUES de que LIBELULA nos haya confirmado el pago exitoso
        # order = request.website.sale_get_order()
        # order.reg_sale()
        # Verificacion de stock de productos
        error = {}
        error_message = {}
        order = request.website.sale_get_order()
        if order:
            lines = order.order_line
            for l in lines:
                l.product_id.consult_stock(l.product_qty)
        return res

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
            if pre_values['ci'] != '' and pre_values['nit'] != '':
                post['ci'] = pre_values['ci']
                post['nit'] = pre_values['nit']
            if pre_values['razon_social'] != '':
                post['razon_social'] = pre_values['razon_social']
            else:
                post['razon_social'] = pre_values['name']
            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)

                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.onchange_partner_id()
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/checkout')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
        }
        return request.render("website_sale.address", render_values)

    @http.route(['/add_event_line'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def event_cart_update(self, product_id,event_line_id, add_qty=1, set_qty=0, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        sale_order._cart_event_update(
            product_id=int(product_id),
            event_line_id=int(event_line_id),
            add_qty=add_qty,
            set_qty=set_qty,
            attributes=self._filter_attributes(**kw),
        )
        return request.redirect("/shop/cart")

    def _get_mandatory_billing_fields(self):
        return ["name", "email", "street", "city", "country_id", 'ci', 'nit', 'razon_social']

    def _get_mandatory_shipping_fields(self):
        return ["name", "street", "city", "country_id", 'ci', 'nit', 'razon_social']

class WebsiteSaleDelivery(WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        order = request.website.sale_get_order()
        carrier_id = post.get('carrier_id')
        if carrier_id:
            carrier_id = int(carrier_id)
        if order:
            order._check_carrier_quotation(force_carrier_id=carrier_id)
            if carrier_id:
                return request.redirect("/shop/payment")

        return super(WebsiteSaleDelivery, self).payment(**post)

    def order_lines_2_google_api(self, order_lines):
        """ Transforms a list of order lines into a dict for google analytics """
        order_lines_not_delivery = order_lines.filtered(lambda line: not line.is_delivery)
        return super(WebsiteSaleDelivery, self).order_lines_2_google_api(order_lines_not_delivery)

    def order_2_return_dict(self, order):
        """ Returns the tracking_cart dict of the order for Google analytics """
        ret = super(WebsiteSaleDelivery, self).order_2_return_dict(order)
        for line in order.order_line:
            if line.is_delivery:
                ret['transaction']['shipping'] = line.price_unit
        return ret

    def _get_shop_payment_values(self, order, **kwargs):
        values = super(WebsiteSaleDelivery, self)._get_shop_payment_values(order, **kwargs)
        has_stockable_products = any(line.product_id.type in ['consu', 'product'] for line in order.order_line)

        if not order._get_delivery_methods() and has_stockable_products:
            values['errors'].append(
                (_('Sorry, we are unable to ship your order'),
                 _('No shipping method is available for your current order and shipping address. '
                   'Please contact us for more information.')))

        if has_stockable_products:
            if order.carrier_id and not order.delivery_rating_success:
                order._remove_delivery_line()

            delivery_carriers = order._get_delivery_methods()
            values['deliveries'] = delivery_carriers.sudo()

        values['delivery_has_stockable'] = has_stockable_products
        values['delivery_action_id'] = request.env.ref('delivery.action_delivery_carrier_form').id
        return values

    def _update_website_sale_delivery(self, **post):
        order = request.website.sale_get_order()
        carrier_id = int(post['carrier_id'])
        if order:
            order._check_carrier_quotation(force_carrier_id=carrier_id)
        return self._update_website_sale_delivery_return(order, **post)

    def _update_website_sale_delivery_return(self, order, **post):
        carrier_id = int(post['carrier_id'])
        currency = order.currency_id
        if order:
            return {'status': order.delivery_rating_success,
                    'error_message': order.delivery_message,
                    'carrier_id': carrier_id,
                    'new_amount_delivery': self._format_amount(order.delivery_price, currency),
                    'new_amount_untaxed': self._format_amount(order.amount_untaxed, currency),
                    'new_amount_tax': self._format_amount(order.amount_tax, currency),
                    'new_amount_total': self._format_amount(order.amount_total, currency),
            }
        return {}
