from odoo import models, fields, api
from datetime import date
import datetime
import codecs
import os
import base64
import contextlib
import io
import csv
import re
# from cStringIO import StringIO
from io import StringIO

try:
    import xlwt
except ImportError:
    xlwt = None


class ReportExp(models.TransientModel):
    _name = "report.export"
    _description = "Descargar Reporte"

    file = fields.Binary(string='Descargar')
    name = fields.Char('File Name')
    filename = fields.Char('File Name')

    @api.multi
    def gen_xls(self, fields, rows, context=None):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(
            context.get('tab', ''), cell_overwrite_ok=True)
        title_style = xlwt.easyxf(
            'font: bold on, height 240; align: wrap off, horiz center')
        label_style = xlwt.easyxf(
            'font: bold on; align: wrap off, horiz right')
        value_style = xlwt.easyxf(
            'font: bold off; align: wrap off, horiz left; borders: bottom thin, top thin, left thin, right thin'
        )

        worksheet.write(0, 7, context.get('title', ''), title_style)
        data = context.get('data', [])
        c = 0
        for i, k in enumerate(data):
            worksheet.write(2, 2 + i + c, k, label_style)
            worksheet.write(2, 3 + i + c, data[k], value_style)
            c += 2
        header_style = xlwt.easyxf(
            'font: bold on; align: wrap yes; borders: bottom medium, top medium, left medium, right medium'
        )
        for i, fieldname in enumerate(fields):
            worksheet.write(3, i, fieldname, header_style)
            worksheet.col(i).width = 5200

        base_style = xlwt.easyxf('align: wrap off')
        date_style = xlwt.easyxf(
            'align: wrap yes', num_format_str='YYYY-MM-DD')
        datetime_style = xlwt.easyxf(
            'align: wrap yes', num_format_str='YYYY-MM-DD HH:mm:SS')
        float_style = xlwt.easyxf('', num_format_str='####.00')

        sum_totals = []
        for row_index, row in enumerate(rows):
            for cell_index, cell_value in enumerate(row):
                cell_style = base_style
                if isinstance(cell_value, str):
                    cell_value = re.sub("\r", " ", cell_value)
                elif isinstance(cell_value, float):
                    cell_style = float_style

                    sum_totals.append(cell_index)
                elif isinstance(cell_value, datetime.datetime):
                    cell_style = datetime_style
                elif isinstance(cell_value, datetime.date):
                    cell_style = date_style
                worksheet.write(row_index + 1, cell_index, cell_value,
                                cell_style)
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data
