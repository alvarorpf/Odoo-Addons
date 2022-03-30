# -*- encoding: utf-8 -*-
from odoo.addons.bus.controllers.main import BusController
from odoo.http import request, route
import io
from PIL import Image
import json
import base64
import logging
from odoo.addons.portal.controllers.mail import PortalChatter
from odoo.tools import consteq, plaintext2html
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo import http, tools, _
from odoo.tools import ustr

_logger = logging.getLogger(__name__)


class ScrumController(BusController):
    # def _poll(self, dbname, channels, last, options):
    #     """Add the relevant channels to the BusController polling."""
    #     if options.get('demo.ticket'):
    #         channels = list(channels)
    #         ticket_channel = (
    #             request.db,
    #             'demo.ticket',
    #             options.get('demo.ticket')
    #         )
    #         channels.append(ticket_channel)
    #     return super(TicketController, self)._poll(dbname, channels, last, options)

    @route(['/scrum'], auth='user', website=True)
    def view_projects(self, **kwargs):
        project_ids = request.env['project.project'].search([])
        return request.render('poi_scrum.scrum_view', {'project': project_ids})

    # @http.route('/poi_scrum/file_upload', type='http',
    #             auth='user', methods=['POST'], website=True)
    # def wsd_upload_file(self, upload, alt='File', filename=None,
    #                     is_image=False, **post_data):
    #     Attachments = request.env['ir.attachment']

    #     # TODO: bound attachemnts to request
    #     try:
    #         data = upload.read()

    #         if is_image:
    #             data = self._optimize_image(data, disable_optimization=False)

    #         attachment = Attachments.create({
    #             'name': alt,
    #             'datas': base64.b64encode(data),
    #             'datas_fname': filename or 'upload',
    #             'public': True,   # TODO: should it be public?
    #             # 'res_model': 'ir.ui.view',
    #         })
    #     except Exception as e:
    #         _logger.exception("Failed to upload file to attachment")
    #         message = ustr(e)
    #         return json.dumps({
    #             'status': 'FAIL',
    #             'success': False,
    #             'message': message,
    #         })

    #     if is_image:
    #         attachment_url = "/web/image/%d/%s" % (
    #             attachment.id,
    #             attachment.datas_fname,
    #         )
    #     else:
    #         attachment_url = "/web/content/%d/%s" % (
    #             attachment.id,
    #             attachment.datas_fname,
    #         )

    #     return json.dumps({
    #         'status': 'OK',
    #         'success': True,
    #         'attachment_url': attachment_url,
    #     })


class PortalChatter(PortalChatter):

    @http.route(['/mail/chatter_post2'], type='json', methods=['POST'], auth='public', website=True)
    def portal_chatter_post(self, res_model, res_id, message, **kw):
        url = request.httprequest.referrer
        if message:
            # message is received in plaintext and saved in html
            message = plaintext2html(message)
            _message_post_helper(res_model, int(res_id), message, **kw)
            url = url + "#discussion"
        return True
