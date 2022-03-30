from odoo import api, fields, models, tools, _
import xmlrpc.client as xc
from odoo.exceptions import UserError


class WsCon(models.Model):
    _name = 'ws.con'

    @api.multi
    def service_connection(self):
        params = self.env['ir.config_parameter'].sudo()
        url_con = params.get_param('poi_x_karlovy_web.url_connection', default='')
        user_con = params.get_param('poi_x_karlovy_web.user_connection', default='')
        password_con = params.get_param('poi_x_karlovy_web.password_connection', default='')
        database_con = params.get_param('poi_x_karlovy_web.database_connection', default='')
        if url_con == '' or user_con == '' or password_con == '' or database_con == '':
            raise UserError("No se cuenta con todos los accesos de conexión entre servidores")
        user_connection = xc.ServerProxy('{}/xmlrpc/common'.format(url_con))
        uid = user_connection.login(database_con, user_con, password_con)
        service = xc.ServerProxy('{}/xmlrpc/object'.format(url_con))
        return database_con, password_con, uid, service
