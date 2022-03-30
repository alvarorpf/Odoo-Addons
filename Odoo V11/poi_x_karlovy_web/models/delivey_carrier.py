from odoo import api, fields, models, tools, _
import xmlrpc.client as xc


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    type_event = fields.Boolean("Delivery de evento")
    type_delivery_event = fields.Selection([('check_in', 'Facturar y envio a novios'), ('send', 'Facturar y recojer en tienda'), ('send_dir', 'Facturar y enviar a dirección')], string='Tipo delivery evento', default="check_in")