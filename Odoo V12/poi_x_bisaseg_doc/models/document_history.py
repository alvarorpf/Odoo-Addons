import logging
import os
import string

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.muk_dms_field.fields import binary

_logger = logging.getLogger(__name__)


class DocumentHistory(models.Model):
    _name = 'document.history'

    def _get_file_name(self):
        try:
            self.env
        except:
            _logger.warning("You are in the wrong Model. Maybe Environment?")
            return False
        valid_chars = "-_.() %s%sÄäÜüÖöß" % (string.ascii_letters, string.digits)
        file_name = "".join(c for c in self.document_id.ref_and_name if c in valid_chars)
        return "{}-{}.{}{}".format('H',file_name, self.version, self.file_ext)

    def _get_file_directory(self):
        try:
            get_param = self.env["ir.config_parameter"].sudo().get_param
            file_directory = get_param("muk_quality_docs_dms.file_directory")
        except:
            try:
                get_param = self["ir.config_parameter"].sudo().get_param
                file_directory = get_param("muk_quality_docs_dms.file_directory")
            except:
                file_directory = False

        if file_directory:
            return int(file_directory)
        else:
            _logger.warning("You have to provide a directory for QMS files.")

    def _get_viewer_file_name(self):
        try:
            self.env
        except:
            _logger.warning("You are in the wrong Model. Maybe Environment?")
            return False
        valid_chars = "-_.() %s%sÄäÜüÖöß" % (string.ascii_letters, string.digits)
        viewer_file_name = "".join(c for c in self.document_id.ref_and_name if c in valid_chars)
        return "{}-{}.{}{}".format(_("VH"), viewer_file_name, self.version, self.viewer_file_ext)

    def _get_viewer_file_directory(self):
        try:
            get_param = self.env["ir.config_parameter"].sudo().get_param
            viewer_file_directory = get_param("muk_quality_docs_dms.viewer_file_directory")
        except:
            try:
                get_param = self["ir.config_parameter"].sudo().get_param
                viewer_file_directory = get_param("muk_quality_docs_dms.viewer_file_directory")
            except:
                viewer_file_directory = False

        if viewer_file_directory:
            return int(viewer_file_directory)
        else:
            _logger.warning("You have to provide a directory for QMS viewer files.")

    @api.depends('document_id')
    def _compute_download(self):
        for r in self:
            if r.official:
                r.download = r.document_id.type_id.downloadable
            else:
                r.download = True

    document_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    user_id = fields.Many2one('res.users', 'Usuario', default=lambda self: self.env.user)
    date = fields.Date('Fecha', default=lambda self: fields.Date.context_today(self))
    version = fields.Char('Versión')
    comment = fields.Char('Comentario')
    official = fields.Boolean('Versión Oficial')
    file = binary.DocumentBinary(filename=_get_file_name, directory=_get_file_directory)
    file_ext = fields.Char("File Extension")
    file_name = fields.Char(compute="_compute_file_name", inverse="_inverse_file_name")
    viewer_file = binary.DocumentBinary(filename=_get_viewer_file_name, directory=_get_viewer_file_directory)
    viewer_file_ext = fields.Char("File Extension")
    viewer_file_name = fields.Char(compute="_compute_viewer_file_name", inverse="_inverse_viewer_file_name")
    preview_name = fields.Char(compute="_compute_preview_name",)
    preview_binary = fields.Binary(compute="_compute_preview_binary",)
    has_preview = fields.Boolean(compute="_compute_preview_binary")
    user_can_only_see_viewer_file = fields.Boolean(compute="_compute_user_can_only_see_viewer_file")
    download = fields.Boolean(compute='_compute_download', store=True)


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

    def _inverse_viewer_file_name(self):
        for record in self:
            if record.viewer_file_name:
                viewer_file_name, viewer_file_extension = os.path.splitext(record.viewer_file_name)
                record.viewer_file_ext = viewer_file_extension
            else:
                record.viewer_file_ext = False

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

    @api.depends("viewer_file_ext")
    def _compute_viewer_file_name(self):
        for record in self:
            if record.viewer_file_ext:
                record.viewer_file_name = record._get_viewer_file_name()
            else:
                record.viewer_file_name = False

    @api.depends("file_name", "viewer_file_name")
    def _compute_preview_name(self):
        for record in self:
            if record.viewer_file:
                record.preview_name = record.viewer_file_name
            elif record.file:
                record.preview_name = record.file_name
            else:
                record.preview_name = False

    @api.depends("file", "viewer_file")
    def _compute_preview_binary(self):
        for record in self:
            value = record.viewer_file or record.file
            record.update({'preview_binary': value, 'has_preview': bool(value)})

    def _compute_user_can_only_see_viewer_file(self):
        normal_user = not self.env.user.has_group("muk_quality_docs.group_muk_quality_docs_author")
        get_param = self.env["ir.config_parameter"].sudo().get_param
        user_can_only_see_viewer_file = get_param("muk_quality_docs_dms.user_can_only_see_viewer_file")
        for record in self:
            ucosvf = normal_user and user_can_only_see_viewer_file and bool(record.viewer_file)
            record.user_can_only_see_viewer_file = ucosvf

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

    @api.onchange("viewer_file_name")
    def _onchange_viewer_file_name(self):
        if self.viewer_file_name:
            viewer_file_name, viewer_file_extension = os.path.splitext(self.viewer_file_name)
            self.viewer_file_ext = viewer_file_extension
        else:
            self.viewer_file_ext = False

    # ===========================================================================
    # Helper Functions
    # ===========================================================================

    def _get_document_context(self):
        context = {}

        if self.file_ext:
            context.update({"default_file_ext": self.file_ext})

        if self.file:
            context.update({"default_file": self.file})

        if self.viewer_file_ext:
            context.update({"default_viewer_file_ext": self.viewer_file_ext})

        if self.viewer_file:
            context.update({"default_viewer_file": self.viewer_file})

        return context

    def is_download(self):
        return True


