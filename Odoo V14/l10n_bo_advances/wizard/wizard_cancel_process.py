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


class WizardCancelProcess(models.TransientModel):
    _name = 'wizard.cancel.process'
    _description = 'Wizard proceso de cancelacion'

    transfer_id = fields.Many2one('internal.transfer')
    ref = fields.Text('Motivo de Rechazo', required=True)

    def action_cancel(self):
        for r in self:
            if not r.transfer_id:
                raise UserError(_("No se pueden cancelar este formulario, debido a que no se encuentra un formulario previo al cual asociar."))
            if r.transfer_id.state == 'deposit':
                for p in r.transfer_id.payment_ids:
                    p.action_draft()
                    p.action_cancel()
            r.transfer_id.write({
                'state': 'cancel',
                })
            r.transfer_id.message_post(body=_(r.ref))
