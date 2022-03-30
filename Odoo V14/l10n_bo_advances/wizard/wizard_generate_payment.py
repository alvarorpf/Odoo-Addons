# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import datetime
import tempfile
import xlwt

from xlwt import Workbook, easyxf
from dateutil.relativedelta import relativedelta
from xlrd import open_workbook
import binascii
import os.path

from collections import defaultdict


class WizardGeneratePayment(models.TransientModel):
    _name = 'wizard.generate.payment'
    _description = 'Wizard de generacion de pago'

    transfer_id = fields.Many2one('internal.transfer')
    journal_origin_id = fields.Many2one('account.journal', "Diario Origen", required=True)
    journal_destiny_id = fields.Many2one('account.journal', "Diario Destino", required=True)
    date = fields.Date('Fecha de pago', required=True)
    ref = fields.Text('Glosa', required=True)

    def action_register(self):
        for r in self:
            if not r.transfer_id:
                raise UserError(_("No se pueden registrar los movimientos contables, debido a que no se encuentra un formulario previo al cual asociar."))
            payment_obj = self.env["account.payment"]
            payment_departure = payment_obj.create({
                'amount': r.transfer_id.amount,
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'date': datetime.date.today(),
                'journal_id': r.journal_origin_id and r.journal_origin_id.id or False,
                'partner_id': self.env.user.company_id.partner_id and self.env.user.company_id.partner_id.id or False,
                'is_internal_transfer': True,
                'ref': r.ref,
                'transfer_id': r.transfer_id.id
            })
            payment_entry = payment_obj.create({
                'amount': r.transfer_id.amount,
                'payment_type': 'inbound',
                'partner_type': 'supplier',
                'date': datetime.date.today(),
                'journal_id': r.journal_destiny_id and r.journal_destiny_id.id or False,
                'partner_id': self.env.user.company_id.partner_id and self.env.user.company_id.partner_id.id or False,
                'is_internal_transfer': True,
                'ref': r.ref,
                'transfer_id': r.transfer_id.id
            })
            payment_departure.action_post()
            payment_entry.action_post()
            r.transfer_id.write({
                'state': 'deposit'
            })
            r.transfer_id.message_post(body=_(r.ref))



