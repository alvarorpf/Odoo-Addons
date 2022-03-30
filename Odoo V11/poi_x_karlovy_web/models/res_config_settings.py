from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    url_connection = fields.Char('Url de conexión')
    user_connection = fields.Char('Usuario de conexión')
    password_connection = fields.Char('Password de conexión')
    database_connection = fields.Char('Base de conexión')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            url_connection=params.get_param('poi_x_karlovy_web.url_connection', default=''),
            user_connection=params.get_param('poi_x_karlovy_web.user_connection', default=''),
            password_connection=params.get_param('poi_x_karlovy_web.password_connection', default=''),
            database_connection=params.get_param('poi_x_karlovy_web.database_connection', default='')
        )
        return res


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('poi_x_karlovy_web.url_connection', self.url_connection)
        self.env['ir.config_parameter'].sudo().set_param('poi_x_karlovy_web.user_connection', self.user_connection)
        self.env['ir.config_parameter'].sudo().set_param('poi_x_karlovy_web.password_connection', self.password_connection)
        self.env['ir.config_parameter'].sudo().set_param('poi_x_karlovy_web.database_connection', self.database_connection)
