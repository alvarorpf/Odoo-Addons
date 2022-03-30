from odoo import models, api, fields, _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def service_get_reserves(self):
        data = []
        stock = self.env['stock.production.lot'].search([('state', '=', 'reserve')])
        if stock:
            for s in stock:
                data.append({
                    'NroReserva': (s.order_line_id and s.order_line_id.name) or False,
                    'FechaReserva': s.fecha_reserva_hasta,
                    'Marca': (s.marca and s.marca.name) or '',
                    'CodModelo': (s.product_id and s.product_id.katashiki.name) or '',
                    'Modelo': (s.product_id and s.product_id.modelo.name) or '',
                    'Master': (s.product_id and s.product_id.master_padre.name) or '',
                    'Año': (s.anio_modelo and s.anio_modelo.name) or '',
                    'Chasis': s.name,
                    'ColorExterno': (s.colorexterno and s.colorexterno.name) or False,
                    'ColorInterno': (s.colorinterno and s.colorinterno.name) or False,
                    'CiCliente': (s.partner_id and s.partner_id.ci) or False,
                    'Nit': (s.partner_id and s.partner_id.nit) or False,
                    'Cliente': (s.partner_id and s.partner_id.name) or False,
                    'Direccion': ((s.partner_id and s.partner_id.street) or '') + '-' + (
                            (s.partner_id and s.partner_id.street2) or ''),
                    'Telefono': (s.partner_id and s.partner_id.phone) or False,
                    'Celular': (s.partner_id and s.partner_id.mobile) or False,
                    'CodVendedor': (s.user_id and s.user_id.id) or '',
                    'Vendedor': (s.user_id and s.user_id.name) or '',
                    'MailVendedor': (s.user_id and s.user_id.login) or False,
                    'TelefonoVendedor': (s.user_id and s.user_id.phone) or False,
                    'Regional': (s.sucursal_id and s.sucursal_id.agency_id.name) or False,
                    'Sucursal': (s.sucursal_id and s.sucursal_id.branch) or False,
                    'Modalidad': (s.currency_id and s.currency_id.name) or False,
                    'PrecioTotal': s.precio_venta,
                    'PorcentajeDescuento': s.descuento,
                    'Banco': (s.bank_id and s.bank_id.name) or False,
                    'Estado': s.state,
                    'Liberado': s.state_finanzas,
                    'Nacionalizado': s.state_importaciones,
                    'Pais': (s.order_line_id.order_id and s.order_line_id.order_id.pais_lugar) or False,
                })
            res = {'Data': data}
            return res
        res = {'Error': 'No se encontro nigun registro'}
        return res
