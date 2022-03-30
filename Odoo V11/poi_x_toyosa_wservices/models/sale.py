from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def service_get_sale_order(self):
        data = []
        orders = self.env['sale.order'].search([])
        if orders:
            for order in orders:
                if order.invoice_ids:
                    r = 'SI'
                else:
                    r = ''
                if order.currency_id:
                    c = 1/order.currency_id.rate
                else:
                    c = ''
                data.append({
                    'FechaCotizacion': order.order_date,
                    'NroCotizacion': order.name,
                    'Marca': (order.lot_id and order.lot_id.product_id.modelo.marca.name) or False,
                    'CodModelo': (order.lot_id and order.lot_id.product_id.katashiki.name) or False,
                    'Modelo': (order.lot_id and order.lot_id.product_id.modelo.name) or False,
                    'Master': (order.lot_id and order.lot_id.product_id.default_code) or False,
                    'Año': (order.lot_id and order.lot_id.anio_modelo.name) or False,
                    'Chasis': (order.lot_id and order.lot_id.name) or False,
                    'ColorExterno': (order.lot_id and order.lot_id.colorexterno.name) or False,
                    'CodColorInterno': (order.lot_id and order.lot_id.colorinterno.name) or False,
                    'CiCliente': (order.partner_id and order.partner_id.ci) or False,
                    'Nit': (order.partner_id and order.partner_id.nit) or False,
                    'Cliente': (order.partner_id and order.partner_id.name) or False,
                    'Direccion': ((order.partner_id and order.partner_id.street) or '') + '-' + (
                            (order.partner_id and order.partner_id.street2) or ''),
                    'Telefono': (order.partner_id and order.partner_id.phone) or False,
                    'Celular': (order.partner_id and order.partner_id.mobile) or False,
                    'CodVendedor': (order.user_id and order.user_id.id) or False,
                    'Vendedor': (order.user_id and order.user_id.name) or False,
                    'MailVendedor': (order.user_id and order.user_id.login) or False,
                    'TelefonoVendedor': (order.user_id and order.user_id.phone) or False,
                    'Regional': (order.warehouse_id.agency_id and order.warehouse_id.agency_id.name) or False,
                    'Sucursal': (order.warehouse_id and order.warehouse_id.branch) or False,
                    'Modalidad': (order.pricelist_id and order.pricelist_id.currency_id.name),
                    'PrecioTotal': order.amount_total,
                    'PorcentajeDescuento': order.discount_percentage,
                    'Banco': order.bank_name,
                    'TipoCambio': c,
                    'Facturado': r,
                })
            res = {
                "Data": data
            }
            return res
        res = {'Error': 'No se encontro nigun registro'}
        return res
