from odoo import fields, models, api
from odoo.exceptions import UserError


class TaxInverse(models.TransientModel):
    _name = 'tax.inverse.wizard'
    _description = "Cálculo precio inverso"

    amount = fields.Float('Precio efectivo', required=True,
                          help="Monto a ser calculado despues de aplicar los Impuestos del caso. Setear el precio para llegar a tal monto.")

    def action_update_price(self):
        context = {}
        if 'invoice_line_id' in self.env.context and self.env.context['invoice_line_id']:
            invoice_line_id = self.env.context['invoice_line_id']
        else:
            return True

        for data in self.read():

            amount = data['amount']

            new_price = 0.0
            tot_tax = 0.0

            iline = self.env['account.move.line'].browse(invoice_line_id)[0]
            if iline.move_id.state != 'draft':
                raise UserError('No es posible calcular un nuevo monto en una Factura ya procesada.')

            invoice_id = iline.move_id
            decimals = iline.move_id.currency_id.decimal_places

            for itax in iline.tax_ids:
                if itax.children_tax_ids:
                    for ichild in itax.children_tax_ids:
                        tot_tax = tot_tax + (1 * abs(ichild.amount))
                else:
                    tot_tax = tot_tax + itax.amount

            new_price = amount / (1 - (tot_tax / 100))
            new_price = round(new_price, decimals)
            if new_price > 0.0:
                iline.with_context(check_move_validity=False).update({'price_unit': new_price})
                iline.move_id.with_context(check_move_validity=False)._recompute_dynamic_lines \
                    (recompute_all_taxes=True, recompute_tax_base_amount=True)
                return True
            else:
                return True
