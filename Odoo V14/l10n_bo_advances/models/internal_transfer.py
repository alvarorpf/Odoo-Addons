# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class InternalTransfer(models.Model):
    _name = 'internal.transfer'
    _description = 'Traspaso Interno'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('send', 'Enviado'),
        ('approved', 'Aprobado'),
        ('deposit', 'Desembolsado'),
        ('cancel', 'Cancelado')], string='Estado', default="draft")
    name = fields.Char('Nombre', default='Nuevo')
    type_id = fields.Many2one('internal.transfer.type', 'Tipo de Operacion', required=True)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', string='Moneda', store=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    employee_id = fields.Many2one('hr.employee', string='Solicitante', compute='_compute_employee', required=True, store=True)
    parent_id = fields.Many2one('hr.employee', 'Responsable', required=True)
    amount = fields.Float("Monto Solicitado", required=True)
    date = fields.Date("Fecha de Solicitud", default=lambda self: datetime.date.today())
    num_transaction = fields.Char("Número de Transacción")
    description = fields.Text("Motivo", required=True)
    expense_report_ids = fields.One2many('hr.expense.sheet', 'advance_id', 'Informes de Gastos')
    is_approver = fields.Boolean("Es Aprobador", compute="_compute_approver")
    payment_ids = fields.One2many("account.payment", "transfer_id", string="Pago")
    type = fields.Selection([('expenses', 'Gastos'), ('refund', 'Reembolsos'), ('other', 'Otros Movimientos')])

    @api.model
    def create(self, vals):
        """
        Herencia de la funcionalidad de creacion para aumentar validaciones de registro y tambien crear la secuencia en base al tipo de movimiento interno configurado
        :param vals:
        :return:
        """
        type = vals.get('type_id')
        if type:
            type_id = self.env['internal.transfer.type'].search([('id', '=', type)])
            if not type_id:
                raise UserError(_("No se encontro un registro coincidente para el tipo"))
            if vals['amount'] < 0.00:
                raise UserError(_('Debe ingresar un monto mayor a 0 para continuar con la operacion.'))
            if vals['amount'] > type_id.max_amount:
                raise UserError(_('Debe ingresar un monto no mayor a %s para continuar con la operacion.' % type_id.max_amount))
            sequence = type_id.sequence_id or False
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code(sequence.code) or '/'
            else:
                vals['name'] = '/'
            return super(InternalTransfer, self).create(vals)
        else:
            raise UserError(_("No se encontro el valor para Tipo de Movimiento, debe seleccionar una opcion."))

    def write(self, vals):
        type = vals.get('type_id', False)
        amount = vals.get('amount', False)
        if type:
            type_id = self.env['internal.transfer.type'].search([('id', '=', type)])
            if not type_id:
                raise UserError(_("No se encontro un registro coincidente para el tipo"))
            if amount:
                if amount < 0.00:
                    raise UserError(_('Debe ingresar un monto mayor a 0 para continuar con la operacion.'))
                if amount > type_id.max_amount:
                    raise UserError(
                        _('Debe ingresar un monto no mayor a %s para continuar con la operacion.' % type_id.max_amount))
        else:
            if amount:
                if amount < 0.00:
                    raise UserError(_('Debe ingresar un monto mayor a 0 para continuar con la operacion.'))
                if amount > self.type_id.max_amount:
                    raise UserError(
                        _('Debe ingresar un monto no mayor a %s para continuar con la operacion.' % self.type_id.max_amount))
        return super(InternalTransfer, self).write(vals)

    @api.depends('user_id')
    def _compute_employee(self):
        """
        Funcion que computa el empleado actual del usuario logueado en el sistema.
        :return:
        """
        user = self.env.user
        employee_id = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        if not employee_id:
            raise UserError(_('El usuario actual no cuenta con un registro como empleado, favor registrarlo'))
        self.employee_id = employee_id and employee_id.id

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
        Funcion que computa el responsable de aprobacion del empleado que esta solicitando la asignacion de fondos
        :return:
        """
        for r in self:
            if r.employee_id and r.employee_id.id:
                if r.employee_id.parent_id and r.employee_id.parent_id.id:
                    r.parent_id = r.employee_id.parent_id.id

    @api.onchange('type')
    def _get_types(self):
        """
        Funcion para filtrar la informacion dependiendo el formulario en el que se encuentra el empleado.
        :return:
        """
        if self.type in ['expenses', 'refund']:
            return {
                'domain': {
                    'type_id':
                        [
                            ('type', '=', self.type)
                        ]
                }
            }

    @api.depends("user_id")
    def _compute_approver(self):
        """
        Funcion para computar si el empleado logueado al sistema puede realizar operaciones de movimientos internos.
        En caso de tener acceso el boton de aprobacion sera visible
        :return:
        """
        for r in self:
            if not r.parent_id:
                approver = True
            elif r.parent_id.user_id.id == self.env.user.id:
                approver = True
            else:
                approver = False
            r.is_approver = approver

    @api.depends('type_id')
    def _compute_currency(self):
        """
        Funcion para computar la moneda en la que se registrara el movimiento interno.
        :return:
        """
        for r in self:
            if r.type_id:
                if r.type_id.journal_departure_id.currency_id:
                    r.currency_id = r.type_id.journal_departure_id.currency_id and r.type_id.journal_departure_id.currency_id.id or False
                else:
                    r.currency_id = self.env.user.company_id.currency_id and self.env.user.company_id.currency_id or False

    def action_send(self):
        """
        Funcion para enviar el movimiento interno para su aprobacion
        :return:
        """
        for r in self:
            r.state = 'send'

    def action_approve(self):
        """
        Funcion para realizar la aprobacion del documento y enviarlo al proceso de registro de pago
        :return:
        """
        for r in self:
            r.state = 'approved'

    def action_cancel(self):
        """
        Funcion para llamar al widget de cancelacion de movimiento interno
        :return:
        """
        return {
            'name': 'Cancelar Operacion',
            'res_model': 'wizard.cancel.process',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'target': 'new',
            'view_type': 'form',
            'context': {
                'default_transfer_id': self.id,
            }
        }

    def action_deposit(self):
        """
        Funcion para llamar al widget para realizar el registro del pago del movimiento interno.
        :return:
        """
        return {
            'name': 'Generacion de Pagos',
            'res_model': 'wizard.generate.payment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'target': 'new',
            'view_type': 'form',
            'context': {
                'default_transfer_id': self.id,
                'default_journal_origin_id': self.type_id.journal_departure_id and self.type_id.journal_departure_id.id or False,
                'default_journal_destiny_id': self.type_id.journal_entry_id and self.type_id.journal_entry_id.id or False,
                'default_date': datetime.date.today(),
                'default_ref': 'Registro de pago para movimiento %s:' % self.name,
            }
        }

    def action_view_payments(self):
        """
        Funcion que apertura el boton inteligente de los pagos registrados para el movimiento interno
        :return:
        """
        return {
            'name': 'Pagos de ' + self.name,
            'domain': [('transfer_id', '=', self.id)],
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {
                'create': False,
                'edit': False,
            }
        }

    def action_view_informs(self):
        """
        Funcion para ver el informe en el cual se encuentra registrado el movimiento interno.
        :return:
        """
        return {
            'name': 'Informes de Gastos ' + self.name,
            'domain': [('advance_id', '=', self.id)],
            'res_model': 'hr.expense.sheet',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {
                'default_advance_id': self.id,
            }
        }




