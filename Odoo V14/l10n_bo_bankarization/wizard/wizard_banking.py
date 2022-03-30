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


class WizardBanking(models.TransientModel):
    _name = 'wizard.banking'
    _description = 'Wizard bancarizacion'

    export_file = fields.Binary(string="Archivo Excel")
    export_filename = fields.Char()
    date_init = fields.Date("Fecha Inicio")
    date_end = fields.Date("Fecha Fin")
    type = fields.Selection([('out_invoice', 'Clientes'), ('in_invoice', 'Proveedores')], string='Tipo')

    def generate_report(self):
        for r in self:
            f_out = tempfile.NamedTemporaryFile()
            book = Workbook(encoding="UTF-8", style_compression=2)
            sheet = book.add_sheet("Bancarizacion")
            sheet = book.get_sheet(0)

            style = self.get_style(height=8, align='right')
            style2 = self.get_style(bold=True, align='center')
            sheet.write_merge(0, 0, 5, 7, "LIBRO AUXILIAR DE COMPRAS PARA REPORTE DE BANCARIZACIÓN, MÓDULO DA VINCI", style=style2)
            col = 2
            row = 3
            sheet.col(0).width = 4000
            sheet.write_merge(col, row, 0, 0, 'Modalidad Transaccion', style=style2)
            sheet.col(1).width = 4000
            sheet.write_merge(col, row, 1, 1, 'Fecha Factura', style=style2)
            sheet.col(2).width = 6000
            sheet.write_merge(col, row, 2, 2, 'Tipo Transacion', style=style2)
            sheet.col(3).width = 9000
            sheet.write_merge(col, row, 3, 3, 'NIT/CI Proveedor', style=style2)
            sheet.col(4).width = 9000
            sheet.write_merge(col, row, 4, 4, 'Nombre/Razon Social Proveedor', style=style2)
            sheet.col(5).width = 9000
            sheet.write_merge(col, row, 5, 5, 'Numero de Factura', style=style2)
            sheet.col(6).width = 9000
            sheet.write_merge(col, row, 6, 6, 'Numero de Contrato', style=style2)
            sheet.col(7).width = 9000
            sheet.write_merge(col, row, 7, 7, 'Importe de Factura', style=style2)
            sheet.col(8).width = 9000
            sheet.write_merge(col, row, 8, 8, 'Numero de Autorización', style=style2)
            sheet.col(9).width = 9000
            sheet.write_merge(col, row, 9, 9, 'Nro. Cuenta del Documento de pago', style=style2)
            sheet.col(10).width = 9000
            sheet.write_merge(col, row, 10, 10, 'Monto de Documento de Pago', style=style2)
            sheet.col(11).width = 9000
            sheet.write_merge(col, row, 11, 11, 'Mondo Acumulado', style=style2)
            sheet.col(12).width = 9000
            sheet.write_merge(col, row, 12, 12, 'NIT Entidad Financiera', style=style2)
            sheet.col(13).width = 9000
            sheet.write_merge(col, row, 13, 13, 'Numero de Documento de Pago', style=style2)
            sheet.col(14).width = 9000
            sheet.write_merge(col, row, 14, 14, 'Tipo de Documento de Pago', style=style2)
            sheet.col(15).width = 9000
            sheet.write_merge(col, row, 15, 15, 'Fecha Documento de Pago', style=style2)
            invoices = self.env['account.move'].search([
                ('move_type', '=', r.type),
                ('invoice_date', '>=', r.date_init),
                ('invoice_date', '<=', r.date_end),
                ('amount_open', '>=', 50000),
                ('state', '=', 'posted')
            ])
            row = 4
            if invoices:
                for i in invoices:
                    sheet.write(row, 0, i.transaction_mod_id.code)
                    sheet.write(row, 1, str(i.invoice_date.month) + '/' + str(i.invoice_date.day) + '/' + str(i.invoice_date.year))
                    sheet.write(row, 2, i.transaction_type_id.code)
                    sheet.write(row, 3, i.nit_ci)
                    sheet.write(row, 4, i.razon_social)
                    sheet.write(row, 5, i.n_factura)
                    sheet.write(row, 6, i.contract_number)
                    sheet.write(row, 7, i.amount_open)
                    sheet.write(row, 8, i.n_autorizacion)
                    sheet.write(row, 9, i.account_number)
                    sheet.write(row, 10, i.amount_open)
                    sheet.write(row, 11, i.amount_open)
                    sheet.write(row, 12, i.nit_origin)
                    sheet.write(row, 13, i.document_number)
                    sheet.write(row, 14, i.document_type_id.code)
                    sheet.write(row, 15, str(i.document_date.month) + '/' + str(i.document_date.day) + '/' + str(i.document_date.year))
                    row += 1
            book.save(f_out)
            f_out.flush()
            self.export_file = base64.b64encode(open(f_out.name, "rb").read())
            self.export_filename = "Bancarizacion.xlsx"
            f_out.close()
            return {
                "type": "ir.actions.act_url",
                "url": "/web/content?model=%s&download=True&field=export_file&id=%s&filename=%s"
                       % (self._name, self.id, self.export_filename),
                "target": "new",
            }


    def get_style(self, bold=False, font_name="Arial", height=10,
            font_color="black", rotation=0, align="left",
            color=None,format=None):
        str_style = "font: bold %s, name %s, height %s, color %s;" % (
            bold,
            font_name,
            height * 20,
            font_color
        )
        str_style += (
            "alignment: rotation %s, horizontal %s,"
            "vertical center, wrap True;" % (rotation, align)
        )
        str_style += color and "pattern: pattern solid, fore_colour %s;" % color or ""
        return easyxf(str_style, num_format_str=format)