# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning


class AccountChargePay(models.TransientModel):
    _name = "account.op.charge.pay"
    _description = 'Pago de cargos'

    def _get_default_dosif(self):
        dosif_users_pool=self.env['poi_bol_base.cc_dosif.users']
        dosif_users_ids=dosif_users_pool.search([('user_id','=',self.env.uid),('user_default','=',True)])
        if dosif_users_ids:
            for dosif_users in dosif_users_ids:
                if dosif_users.dosif_id.activa and dosif_users.dosif_id.applies == 'out_invoice':
                    return dosif_users.dosif_id.id

    #do_invoice = fields.Boolean('')
    charge_ids = fields.Many2many('account.op.charge', string='Cargos', required=True)
    date = fields.Date('Fecha', default=fields.Date.today(), required=True)
    dosif_id = fields.Many2one('poi_bol_base.cc_dosif', string='Dosificación', default=_get_default_dosif, help=u"Serie de dosificación según parametrización. Asocia Número de autorizacción y Llave de dosificación.")
    nit = fields.Char('NIT', size=12, help="NIT o CI del cliente.")
    razon = fields.Char(u'Razón Social', help=u"Nombre o Razón Social para la Factura.")
    warehouse_id = fields.Many2one('stock.warehouse', string=u'Almacén')
    journal_id = fields.Many2one('account.journal', string=u'Método de pago')

    @api.model
    def default_get(self, fields):
        res = super(AccountChargePay, self).default_get(fields)
        nit=False
        rs=False
        charge_ids = self.env.context.get('charge_ids', [])
        res['charge_ids'] = charge_ids
        for charge in self.env['account.op.charge'].browse(charge_ids):
            responsable = charge.student_id.payment_responsable
            nit = responsable.partner_id.ci or responsable.partner_id.nit or False
            rs = responsable.partner_id.razon or False


        res['nit'] = nit
        res['razon'] = rs

        return res

    @api.one
    def action_generate(self):

        charge_obj = self.env['op.request.charge']

        charges = []
        charges_to_check = []
        student_id = False
        family_code = False
        responsable = False
        for charge in self.charge_ids:
            charge_line = {
                'check': True,
                'charge_id': charge.id,
                'product_id': charge.product_id and charge.product_id.id or False,
                'date': charge.date,
                'date_due': charge.date_due,
                'type': charge.product_id and charge.product_id.concept_type or False,
                'amount_untaxed': charge.amount_untaxed,
                'amount_tax': charge.amount_tax,
                'amount_total': charge.amount_total,
            }
            charges.append((0, 0, charge_line))
            charges_to_check.append(charge.id)
            #ToDo: Validar consistencia de mismo Alumno/Resp, gestion, Estados!
            student_id = charge.student_id.id
            code_family = charge.family_id.id
            responsable = charge.student_id.payment_responsable
            year_id = charge.year_id.id
            currency_id = charge.currency_id.id

        #Crear Request Charge
        request_charges = charge_obj.create({
            'student_id': student_id,
            'code_family': code_family,
            'responsable_id': responsable.id,
            'year_id': year_id,
            'currency_id': currency_id,
            'date': self.date,
            'date_due': self.date,
            #'line_ids': charges,
        })

        #Facturar y validar factura
        request_charges.onchange_student_id()
        request_charges._compute_partner_id()
        request_charges._compute_currency_id()
        for line in request_charges.line_ids:
            if line.charge_id.id in charges_to_check:
                line.write({'check': True})
        request_charges._compute_amount_total()
        request_charges.action_confirm_charge()
        if request_charges.invoice_id:
            request_charges.invoice_id.write({'cc_dos': self.dosif_id.id, 'nit': self.nit})
            request_charges.invoice_id.action_invoice_open()

            #Pagar factura
            context = dict(self.env.context or {})
            context['default_journal_id'] = self.journal_id.id
            # return request_charges.action_pay_charge()

            payment = self.env['account.payment'].create({
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'payment_date': self.date,
                'journal_id': self.journal_id.id,
                'payment_method_id': self.journal_id.inbound_payment_method_ids and self.journal_id.inbound_payment_method_ids[0].id or False,
                'amount': request_charges.invoice_id.amount_total,
                'charge_request_id': request_charges.id,
                'invoice_ids': [(4, request_charges.invoice_id.id, None)],
                'partner_id': request_charges.invoice_id.partner_id.id,
                'currency_id': self.journal_id.currency_id.id or self.journal_id.company_id.currency_id.id,
                'communication': 'Pago de cargos ' + request_charges.invoice_id.number or '',
            })
            payment.post()
            request_charges.write({'payment_id': payment.id})


        #Abrir formulario
        views = [(self.env.ref('poi_x_aleman.op_request_charge_view_form').id, 'form'),
                 (self.env.ref('poi_x_aleman.op_request_charge_view_tree').id, 'tree')]
        action_result = {
            'name': 'Pago de cargo',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'view_id': self.env.ref('poi_x_aleman.op_request_charge_view_form').id,
            'views': views,
            'res_model': 'op.request.charge',
            'target': 'current',
            'res_id': request_charges.id,
            'type': 'ir.actions.act_window',
        }
        return action_result

