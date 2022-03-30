from odoo import models, api, fields, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def service_get_stock(self):
        data = []
        stock = self.env['stock.production.lot'].search([])
        if stock:
            for s in stock:
                data.append({
                    'Modelos': (s.category and s.category.name) or '',
                    'CodMarca': (s.marca and s.marca.id) or '',
                    'Marca': (s.marca and s.marca.name) or '',
                    'CodModelo': (s.product_id and s.product_id.katashiki.name) or '',
                    'Modelo': (s.product_id and s.product_id.modelo.name) or '',
                    'Codmaster': (s.product_id and s.product_id.master_padre.id) or '',
                    'Master': (s.product_id and s.product_id.master_padre.name) or '',
                    'Año': (s.anio_modelo and s.anio_modelo.name) or '',
                    'CodColorExterno': (s.colorexterno and s.colorexterno.id) or False,
                    'ColorExterno': (s.colorexterno and s.colorexterno.name) or False,
                    'CodColorInterno': (s.colorinterno and s.colorinterno.id) or False,
                    'ColorInterno': (s.colorinterno and s.colorinterno.name) or False,
                    'Chasis': s.name,
                    'CodUbicacion': (s.location_id and s.location_id.cod_ubicacion) or False,
                    'Ubicacion': (s.location_id and s.location_id.name) or False,
                    'NomLocalidad': 1,
                    'Vendedor': (s.user_id and s.user_id.name) or '',
                    'Lugar': (s.user_id and s.user_id.shop_assigned.name) or False,
                    'Estado': s.state,
                    'Liberado': s.state_finanzas,
                    'Nacionalizado': s.state_importaciones,
                    'Pais': (s.order_line_id.order_id and s.order_line_id.order_id.pais_lugar) or False,
                    'TipoUnidad': (s.product_uom_id and s.product_uom_id.name),
                })

            res = {
                "Data": data,
            }
            return res
        res = {"Error": "No se encontro ningun registro"}
        return res
