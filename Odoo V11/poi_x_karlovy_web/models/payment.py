# coding: utf-8

import logging
from odoo import api, fields, models, _


class TxLibelula(models.Model):
    _inherit = 'payment.transaction'

    def _libelula_form_validate(self, data):

        validated = super(TxLibelula, self)._libelula_form_validate(data=data)
        if validated:
            reference = data.get('transaction_id')

            factura_id = self.env['dosificacion.todotix.factura'].sudo().search([('unique_id', '=', reference)])
            is_paid = factura_id.consulta_deuda_pagada()

            if is_paid and self.sale_order_id:
                self.sale_order_id.reg_sale()

        return validated
