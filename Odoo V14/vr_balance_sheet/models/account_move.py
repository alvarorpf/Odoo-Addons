# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'

    period_id = fields.Many2one("account.period", "Periodo Contable", compute='_compute_period', store=True)

    @api.depends("date")
    def _compute_period(self):
        for r in self:
            date = r.date
            period_obj = self.env['account.period']
            if date:
                period = period_obj.search([('date_init', '<=', date), ('date_end', '>=', date)])
            else:
                date = datetime.date.today()
                period = period_obj.search([('date_init', '<=', date), ('date_end', '>=', date)])
            if period:
                if period.state == "close":
                    raise UserError(
                            _("El periodo contable correspondiente al mes en curso se encuentra cerrado, aperturelo para continuar con el registro del asiento contable."))
                elif period.state == "draft":
                    raise UserError(
                            _("El periodo contable correspondiente al mes en curso se encuentra en estado borrador, aperturelo para continuar con el registro del asiento contable."))
            # else:
            #     raise UserError(
            #             _("No se encontro un registro para el periodo contable actual, realizar la creación del mismo."))
            r.period_id = period and period.id or False

    def write(self, vals):
        """
        Validación para la edición de asientos contables en base a periodo contable cerrado y roles de usuarios
        :param vals:
        :return:
        """
        count = 0
        for r in self:
            if self.env.user.has_group('account.group_account_manager') and r.period_id.state == "close":
                continue
            elif self.env.user.has_group('account.group_account_user') and r.period_id.state == "close":
                raise UserError(_("No se puede realizar la modificación de este asiento contable. El periodo contable se encuentra cerrado."))

        return super(AccountMove, self).write(vals)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    user_type_id = fields.Many2one('account.account.type', related="account_id.user_type_id", readonly="1")