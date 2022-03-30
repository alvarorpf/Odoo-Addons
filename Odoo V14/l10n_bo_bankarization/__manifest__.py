# -*- coding: utf-8 -*-
{
    'name': "l10n_bo_bankarization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Alvaro Renato Paredes Flores",
    'website': "https://versatil.com.bo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['l10n_bo_invoice', 'l10n_bo_lcv'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        'views/banking_document_type_view.xml',
        'views/banking_transaction_mod_view.xml',
        'views/banking_transaction_type_view.xml',
        'wizard/wizard_banking.xml',
        'wizard/account_payment_register.xml'
    ],
}
