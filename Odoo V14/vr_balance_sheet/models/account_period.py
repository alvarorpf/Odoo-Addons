# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

months = ['Enero', 'Febrero', 'Marzo',
          'Abril', 'Mayo', 'Junio',
          'Julio', 'Agosto', 'Septiembre',
          'Octubre', 'Noviembre', 'Diciembre']


class AccountPeriod(models.Model):
    _name = 'account.period'
    _description = 'Periodo Contable'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ("draft", "Borrador"),
        ("open", "Abierto"),
        ("close", "Cerrado")], string="Estado", default="draft", track_visibility="onchange")
    name = fields.Char("Nombre", required=True, default="Nuevo")
    date_init = fields.Date("Fecha de Inicio", required=True)
    date_end = fields.Date("Fecha Fin")
    date_update = fields.Datetime("Última Actualización")
    description = fields.Text("Glosa")
    user_id = fields.Many2one('res.users', 'Usuario', default=lambda self: self.env.user)

    @api.model
    def create(self, vals):
        """
        Validacion para la creación de periodos contables repetidos por mes
        :param vals:
        :return:
        """
        period_obj = self.env["account.period"]
        period_id = period_obj.search([
            ('date_init', '>=', vals['date_init']),
            ('date_end', '<=', vals['date_end']),
        ])
        if period_id:
            raise UserError(
                _("Ya existe un formulario registrado para el siguiente rango de fechas (%s - %s)"
                  % (datetime.datetime.strptime(vals['date_init'], '%Y-%m-%d').strftime('%d/%m/%Y'),
                      datetime.datetime.strptime(vals['date_end'], '%Y-%m-%d').strftime('%d/%m/%Y'))
                  )
            )
        res = super(AccountPeriod, self).create(vals)
        return res

    def unlink(self):
        """
        Validación para evitar la eliminación de los periodos contables aperturados o cerrados
        :return:
        """
        for r in self:
            if r.state in ["open", "close"]:
                raise UserError(_("No se puede eliminar un periodo contable Aperturado/Cerrado."))
            return super(AccountPeriod, self).unlink()

    @api.onchange('date_init')
    def onchange_date_init(self):
        """
        Función para la asignación de fechas.
        Asigna el primer dia del mes al campo fecha inicio.
        Asigna el último dia del mes al campo fecha fin.
        :return:
        """
        for r in self:
            if r.date_init:
                date = r.date_init
                date_init = date.replace(day=1)
                date_end = r.last_day_of_month(date)
                r.date_init = date_init
                r.date_end = date_end

    def last_day_of_month(self, any_day):
        """
        Función para la obtención del último día del mes en base a una fecha dada
        :param any_day:
        :return:
        """
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    def action_open_period(self):
        """
        Función para realizar la apertura del periodo contable
        :return:
        """
        for r in self:
            if r.state == "draft":
                r.state = "open"
                month = r.date_init.month
                year = r.date_init.year
                month_l = months[month-1]
                name = "%s/%s" % (month_l, year)
                r.name = name
                r.date_update = datetime.datetime.now()
            elif r.state == "close":
                r.state = "open"
                r.date_update = datetime.datetime.now()

    def action_close_period(self):
        """
        Función para realizar el cierre de un periodo contable
        :return:
        """
        for r in self:
            moves = self.env['account.move'].search([('state', '=', 'draft'), ('period_id', '=', r.id)])
            if moves:
                raise UserError(_('Existen movimientos contables en estado Borrador, para cerrar el periodo contable debera cancelar estos movimientos.'))
            if r.state == "open":
                r.state = "close"
                r.date_update = datetime.datetime.now()

    def action_view_moves(self):
        return {
            'name': 'Asientos Contables',
            'domain': [('period_id', '=', self.id)],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {
                'default_move_type': 'entry',
                'group_by': ['state'],
            }
        }


