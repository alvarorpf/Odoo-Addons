from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    """
    Campos de cuentas para realziar el anticipo a clientes y proveedores
    """
    property_prepaid_account_payable_id = fields.Many2one('account.account', company_dependent=True,
                                                 string="Cuenta por cobrar(Anticipo)",
                                                 domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]")
    property_prepaid_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
                                                    string="Cuenta por pagar (Anticipo)",
                                                    domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False),('company_id', '=', current_company_id)]")