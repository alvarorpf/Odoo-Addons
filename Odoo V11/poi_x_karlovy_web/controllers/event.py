from odoo import http

from addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from werkzeug.exceptions import Forbidden, NotFound


class Event(http.Controller):

    @http.route('/events', type='http', auth='public', website=True)
    def event_list(self, **kwargs):
        return request.render('poi_x_karlovy_web.lista_eventos_karlovy', {})

    @http.route('/event_search', type='http', methods=['GET'], auth="public", website=True)
    def event_search(self, **kwargs):
        search = kwargs['search']
        event_list = []
        if search != '':
            event_list = request.env['ws.event.11'].sudo().search([('name', 'ilike', search), ('type_event', 'in', ['BODA'])], order="date_start asc")
        return request.render('poi_x_karlovy_web.lista_eventos_karlovy', {'events': event_list})

    @http.route('/events/<int:event_id>', type='http', auth='public', website=True)
    def event_lines(self, event_id, **kwargs):
        event = request.env['ws.event.11'].sudo().search([('id', '=', event_id)], order="date_start asc")
        lines = event.line_ids
        return request.render('poi_x_karlovy_web.regalos_karlovy', {'lines': lines, 'event': event})

    @http.route('/events/<int:event_id>/event_purchase/<int:line_id>', type='http', auth='public', website=True)
    def event_purchase(self, event_id, line_id, **kwargs):
        deliveries = request.env['delivery.carrier'].sudo().search([('type_event', '=', True), ('active', '=', True)])
        product = request.env['ws.event.lines.11'].sudo().search([('id', '=', int(line_id))]).product_id
        return request.render('poi_x_karlovy_web.reserva_regalo_karlovy', {'line': line_id, 'event': event_id,'deliveries': deliveries, 'product': product})

    @http.route('/event_purchase', type='http', methods=['POST'], auth="public", website=True)
    def event_purchase_confirm(self, **kwargs):
        values = kwargs
        event = request.env['ws.event.11'].sudo()
        event.reg_purchase(values)
        product = request.env['ws.event.lines.11'].sudo().search([('id', '=', values['line'])]).product_id
        delivery = request.env['delivery.carrier'].sudo().search([('id', '=', values['delivery_type'])]).product_id
        return request.render('poi_x_karlovy_web.agradecimientos_karlovy', {'product': product, 'delivery': delivery})
