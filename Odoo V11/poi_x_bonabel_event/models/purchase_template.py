# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _


class PurchaseOrderEmbalaje(models.Model):
    _name = 'purchase.order.embalaje'

    name = fields.Char("Forma Embalaje")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fields_test1 = fields.Char("Pais/lugar")
    fields_test2 = fields.Char("Pais/lugar")
