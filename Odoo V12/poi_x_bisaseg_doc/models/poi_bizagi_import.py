from odoo import models, fields, api, _
import base64
from io import BytesIO
import os
from zipfile import ZipFile
import shutil

# ruta de la carpeta en el servidor
ROOT_FILE = "/var/www/"
BASE_URL = "http://192.168.11.118:8080/"


class PoiBizagiImportWizard(models.TransientModel):
    _name = 'poi.bizagi.import.wizard'

    files = fields.Binary(string="Archivo (.Zip)", attachment=False, prefetch=False)

    @api.multi
    def import_files(self):
        code = self.env['ir.sequence'].next_by_code('poi.bizagi.import') 
        bizagi_obj = self.env['poi.bizagi.import']
        zip_data = base64.decodestring(self.files)
        model = self.env.context.get('active_model', False)
        res_id = self.env.context.get('active_id', False)
        bizagi_id = bizagi_obj.create({
            'ruta': ROOT_FILE + code,
            'url': BASE_URL + code,
            'code': code,
            'model': model,
            'res_id': res_id,
        })
        if model and res_id:
            obj_id = self.env[model].browse(res_id)
            obj_id.url = bizagi_id.url
        fp = BytesIO()
        fp.write(zip_data)
        with ZipFile(fp, "r") as z:
            z.extractall(ROOT_FILE)
            root, file_name = z.filelist[0].filename.split('/', 2)
            shutil.move(ROOT_FILE + root, ROOT_FILE + code)
        return bizagi_id


class PoiBizagiImportWizard(models.Model):
    _name = 'poi.bizagi.import'
    _rec_name = 'code'

    ruta = fields.Char('Ruta Archivo')
    url = fields.Char('Url Generada')
    code = fields.Char('Código Generado')
    model = fields.Char('Modelo')
    res_id = fields.Char('Id del modelo')
