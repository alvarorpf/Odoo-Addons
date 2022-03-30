# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Saritha Sahadevan (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
import csv
import urllib
import base64
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from odoo import models, fields, api
import base64
import os

class DocumentImportWizard(models.TransientModel):
    _name = 'import.document'

    dir = fields.Char('Directorio Tabla')
    dir_files = fields.Char('Directorio Archivos')

    @api.multi
    def import_file(self):
        with open(self.dir, newline='') as File:
            reader = csv.reader(File)
            header = True
            error = []
            for row in reader:
                if header:
                    header = False
                else:
                    document = self.env['muk_quality_docs.document']
                    doc = document.search([('name', '=', row[0])])
                    path = self.dir_files + row[1]
                    try:
                        with open(path, 'rb') as archivo:
                            object = base64.encodebytes(archivo.read())
                            if doc and object:
                                doc.viewer_file = object
                                doc.preview_binary = object
                    except:
                        error.append(row[1])
                if len(error) >= 1:
                    file = open(self.dir_files + "errores.txt", "w")
                    for e in error:
                        file.write('Documento:' + e + os.linesep)
                    file.close()

