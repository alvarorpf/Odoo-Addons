from odoo import api, fields, exceptions, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def service_get_invoices(self):
        data = []
        invoices = self.env['account.invoice'].search([])
        if invoices:
            for invoice in invoices:
                data.append({
                    'NroFactura': (invoice and invoice.number) or '',
                    'FechaFactura': invoice.date_invoice,
                    'Marca': (invoice.lot_id and invoice.lot_id.product_id.modelo.marca.name) or False,
                    'CodModelo': (invoice.lot_id and invoice.lot_id.product_id.katashiki.name) or False,
                    'Modelo': (invoice.lot_id and invoice.lot_id.product_id.modelo.name) or False,
                    'Master': (invoice.lot_id and invoice.lot_id.product_id.default_code) or False,
                    'Año': (invoice.lot_id and invoice.lot_id.anio_modelo.name) or False,
                    'Chasis': (invoice.lot_id and invoice.lot_id.name) or False,
                    'ColorExterno': (invoice.lot_id and invoice.lot_id.colorexterno.name) or False,
                    'ColorInterno': (invoice.lot_id and invoice.lot_id.colorinterno.name) or False,
                    'CiCliente': (invoice.partner_id and invoice.partner_id.ci) or False,
                    'Nit': (invoice.partner_id and invoice.partner_id.nit) or False,
                    'Cliente': (invoice.partner_id and invoice.partner_id.name) or False,
                    'Direccion': ((invoice.partner_id and invoice.partner_id.street) or '') + '-' + (
                            (invoice.partner_id and invoice.partner_id.street2) or ''),
                    'Telefono': (invoice.partner_id and invoice.partner_id.phone) or False,
                    'Celular': (invoice.partner_id and invoice.partner_id.mobile) or False,
                    'CodVendedor': (invoice.user_id and invoice.user_id.id) or False,
                    'Vendedor': (invoice.user_id and invoice.user_id.name) or False,
                    'MailVendedor': (invoice.user_id and invoice.user_id.login) or False,
                    'TelefonoVendedor': (invoice.user_id and invoice.user_id.phone) or False,
                    'Regional': (invoice.warehouse_id.agency_id and invoice.warehouse_id.agency_id.name) or False,
                    'Sucursal': (invoice.warehouse_id and invoice.warehouse_id.branch) or False,
                    'PrecioBolivianos': invoice.amount_total,
                })
            res = {
                "Data": data
            }
            return res
        res = {'Error': 'No se encontro nigun registro'}
        return res
