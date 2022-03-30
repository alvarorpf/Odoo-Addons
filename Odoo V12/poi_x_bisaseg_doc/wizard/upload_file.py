import logging
import os
import string

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.muk_dms_field.fields import binary

_logger = logging.getLogger(__name__)


class UploadFile(models.TransientModel):
    _name = 'upload.file'

    def _get_file_name(self):
        try:
            self.env
        except:
            _logger.warning("You are in the wrong Model. Maybe Environment?")
            return False
        valid_chars = "-_.() %s%sÄäÜüÖöß" % (string.ascii_letters, string.digits)
        file_name = "".join(c for c in self.document_id.ref_and_name if c in valid_chars)
        return "{}.{}{}{}".format(file_name, self.version, 'H', self.file_ext)

    @api.depends('document_id', 'official')
    def _compute_version(self):
        for r in self:
            if r.document_id:
                version = r.document_id.version_work
                v = version.split('.')
                if r.official:
                    v[0] = str(int(v[0]) + 1)
                    v[1] = str(0)
                    v[2] = str(0)
                else:
                    if r.user_id.has_group('poi_x_bisaseg_doc.group_o_and_m'):
                        v[1] = str(int(v[1]) + 1)
                        v[2] = str(0)
                    else:
                        v[2] = str(int(v[2]) + 1)
                r.version = '.'.join(v)

    document_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    user_id = fields.Many2one('res.users', 'Usuario', default=lambda self: self.env.user)
    date = fields.Date('Fecha', default=lambda self: fields.Date.context_today(self))
    version = fields.Char('Versión', compute='_compute_version', store=True)
    comment = fields.Char('Comentario')
    file = fields.Binary('Archivo')
    file_ext = fields.Char("File Extension")
    file_name = fields.Char(compute="_compute_file_name", inverse="_inverse_file_name")
    official = fields.Boolean('Versión Oficial')

    # ===========================================================================
    # Inverse Functions
    # ===========================================================================

    def _inverse_file_name(self):
        for record in self:
            if record.file_name:
                file_name, file_extension = os.path.splitext(record.file_name)
                record.file_ext = file_extension
            else:
                record.file_ext = False

    # ===========================================================================
    # Computed Functions
    # ===========================================================================

    @api.depends("file_ext")
    def _compute_file_name(self):
        for record in self:
            if record.file_ext:
                record.file_name = record._get_file_name()
            else:
                record.file_name = False

    @api.depends("file_name")
    def _compute_preview_name(self):
        for record in self:
            if record.file:
                record.preview_name = record.file_name
            else:
                record.preview_name = False

    # ===========================================================================
    # OnChange Functions
    # ===========================================================================

    @api.onchange("file_name")
    def _onchange_file_name(self):
        if self.file_name:
            file_name, file_extension = os.path.splitext(self.file_name)
            self.file_ext = file_extension
        else:
            self.file_ext = False

    def action_continue(self):
        for r in self:
            document = r.document_id
            if document:
                history = self.env['document.history']
                if r.official:
                    document.sudo().write({'preview_binary': r.file, 'viewer_file': r.file, 'viewer_file_ext': r.file_ext, 'work_on_file': True, 'last_version_date': fields.Date.context_today(self)})
                    h = history.create({
                        'document_id': r.document_id.id,
                        'user_id': r.user_id.id,
                        'date': r.date,
                        'version': r.version,
                        'comment': r.comment,
                        'viewer_file': r.file,
                        'viewer_file_ext': r.file_ext,
                        'viewer_file_name': r.file_name,
                    })
                else:
                    h = history.create({
                        'document_id': r.document_id.id,
                        'user_id': r.user_id.id,
                        'date': r.date,
                        'version': r.version,
                        'comment': r.comment,
                        'file': r.file,
                        'file_ext': r.file_ext,
                        'file_name': r.file_name,
                    })
                if h:
                    document.sudo().write({'version_work': r.version})
                else:
                    raise UserError('No se pudo realizar la carga del archivo.')
