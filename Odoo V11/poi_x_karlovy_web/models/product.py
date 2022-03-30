# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
import xmlrpc.client as xc
import logging
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = "product.product"

    v7_id = fields.Integer('ID version 7')

    @api.model
    def consult_stock(self, qty):
        for s in self:
            con = self.env['ws.con']
            db, pwd, uid, service = con.service_connection()
            product = service.execute(db, uid, pwd, 'ws.product', 'search', [('product_id', '=', s.v7_id)])
            data = service.execute(db, uid, pwd, 'ws.product', 'read', product, [])
            if data:
                if int(qty) > int(data[0]['qty']):
                    raise ValidationError(_("El producto no cuenta con esta cantidad de stock disponible por favor vuelva a intentar con otra cantidad."))

    @api.model
    def sync_ventas(self):
        sale_obj = self.env['sale.order']
        sales = sale_obj.search([('web_sale', '=', True), ('sale_error', '=', True)])
        # Log de actualizacion deproductos
        _logger.debug("___________________________________________________________")
        _logger.debug("             Cron de Actualizacion Ventas")
        _logger.debug("-----------------------------------------------------------")
        if sales:
            for s in sales:
                s.reg_sale()

    @api.model
    def sync_product(self):
        sale_obj = self.env['sale.order']
        sales = sale_obj.search([('web_sale', '=', True), ('sale_error', '=', True)])
        # Log de actualizacion deproductos
        _logger.debug("___________________________________________________________")
        _logger.debug("             Cron de Actualizacion de Productos")
        _logger.debug("-----------------------------------------------------------")
        if sales:
            for s in sales:
                s.reg_sale()
        con = self.env['ws.con']
        db, pwd, uid, service = con.service_connection()
        prods = self.env['product.product'].search([])
        a_prod = []
        for p in prods:
            if p.v7_id:
                a_prod.append(p.v7_id)
        products = service.execute(db, uid, pwd, 'ws.product', 'search',
                                   [('product_id', 'in', a_prod)])#a_prod [13292,13305]

        # Log de cantidad de productos por actualizarse
        _logger.debug("Cantidad de productos: " + str(len(products)))
        bob_currency = self.env.ref('base.BOB')
        usd_currency = self.env.ref('base.USD')
        # Inicializacion al contador de actualizacion de productos
        count = 1
        for p in products:
            data = service.execute(db, uid, pwd, 'ws.product', 'read', p, [])
            product = self.env['product.product'].search([('default_code', '=', data['code']), ('product_tmpl_id.active', '=', True)])
            if product:
                # Log de Producto
                _logger.debug("Actualización de Producto")
                _logger.debug("Código Producto: " + str(data['code']))
                _logger.debug("Nombre Producto: " + str(data['description']))
                _logger.debug("Stock Producto: " + str(data['qty']))
                product = product[0]
                product.name = data['description']
                product.product_tmpl_id.name = data['description']
                product.image = data['img']
                _logger.debug("Actualizado imagen template: ")
                product.product_tmpl_id.image = data['img']
                price = usd_currency.compute(data['price'], bob_currency)
                product.list_price = price
                product.list_price_second = data['price']
                if product.v7_id != data['product_id']:
                    product.v7_id = data['product_id']
                if data['qty'] > 0:
                    product.website_published = True
                    _logger.debug("Producto activo en sitio web")
                else:
                    product.website_published = False
                    _logger.debug("Producto inactivo en sitio web")

                # Incremento de contador
                count += 1
                self.env.cr.commit()
        _logger.debug("Cantidad de productos actualizados o creados: " + str(count))
        # Productos Inactivos Sincronizados
        products2 = service.execute(db, uid, pwd, 'product.product', 'search', [('active', '=', False)])
        for p in products2:
            data = service.execute(db, uid, pwd, 'product.product', 'read', p, ['active', 'code', 'id'])
            product = self.env['product.product'].search(
                [('default_code', '=', data['code']), ('v7_id', '=', data['id']), ('product_tmpl_id.active', '=', True), ('product_tmpl_id.website_published', '=', True)])
            if product:
                product.website_published = False
                self.env.cr.commit()

    @api.model
    def sync_new_products(self):
        _logger.debug("___________________________________________________________")
        _logger.debug("           Cron de Actualizacion de Productos Nuevos       ")
        _logger.debug("-----------------------------------------------------------")
        con = self.env['ws.con']
        db, pwd, uid, service = con.service_connection()
        prods = self.env['product.product'].search([])
        a_prod = []
        for p in prods:
            if p.v7_id:
                a_prod.append(p.v7_id)
        products = service.execute(db, uid, pwd, 'ws.product', 'search',
                                   [('product_id', 'not in', a_prod)])
        bob_currency = self.env.ref('base.BOB')
        usd_currency = self.env.ref('base.USD')
        for p in products:
            data = service.execute(db, uid, pwd, 'ws.product', 'read', p, [])
            data2 = service.execute(db, uid, pwd, 'product.product', 'read', data['product_id'], [])
            product_obj = self.env['product.product']
            line_id = self.env['linea.producto'].search([('name', '=', data2['line_product'][1])])
            _logger.debug("Creación de Producto Nuevo")
            _logger.debug("Código Producto: " + str(data['code']))
            _logger.debug("Nombre Producto: " + str(data['description']))
            _logger.debug("Stock Producto: " + str(data['qty']))
            if data['qty'] > 0:
                published = True
                _logger.debug("Producto activo en sitio web")
            else:
                published = False
                _logger.debug("Producto inactivo en sitio web")
            price = usd_currency.compute(data2['list_price_second'], bob_currency)
            product_obj.create({
                'name': data2['name_template'],
                'list_price': price,
                'list_price_second': data2['list_price_second'],
                # 'barcode': data['ean13'],
                'default_code': data2['code'],
                'company_id': 1,
                'producto': data2['producto'],
                'image': data2['image'],
                'sale_ok': True,
                'purchase_ok': True,
                'dimension': data2['dimension'],
                'line_product': line_id and line_id.id or False,
                'categ_id': 1,
                'type': 'product',
                'website_published': published,
                'v7_id': data['product_id']
            })
            # Incremento de contador
            self.env.cr.commit()