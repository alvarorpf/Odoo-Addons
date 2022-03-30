# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import base64


try:
    import xlwt
except ImportError:
    xlwt = None


class GeneralLedgerAleman(models.TransientModel):
    _name = "general.ledger.aleman.wizard"

    company_id = fields.Many2one('res.company', 'Compañia')
    currency_id = fields.Many2one('res.currency', 'Moneda')
    date_ini = fields.Date('Fecha Desde')
    date_end = fields.Date('Fecha Hasta', default=fields.Datetime.now)
    adjust = fields.Selection([('with_adjust', 'Con Ajuste'), ('not_adjust', 'Sin Ajuste')], 'Tipo de Informacion')

    @api.multi
    def generate_report(self):
        data = self.read()[0]
        return self.env.ref('poi_x_aleman.potential_income_report').report_action(self, data=data)

    # Funcion para el armado del reporte en excel en base a parametrizacion
    # value: Devuelve el padre/hijo
    # info: Datos obtenidos con el query
    # array: Array general donde se arma el reporte
    # count: Contador base para dibujar las lineas del reporte
    # cell: Array hijo de ultimo nivel donde se actualizara los valores
    # money: Moneda en la que se realizara el reporte
    # val: valor para la eliminacion de caracteres del teclado para la obtencion de la informacion
    # balance: Diccionario para sumar los totalizadores
    # company_id: compañia para la cual se armara el reporte, en caso de no contar con valor armara el combinado

    @api.multi
    def array_recursive(self, value, info, money, val, balance, company_id=False):
        if len(value.children_ids) > 0:
            for child in value.children_ids:
                balance.update({
                    child.code: {
                        "value": 0,
                        "level": child.level,
                        'name': child.name,
                    }
                })
                self.array_recursive(child, info, money, val, balance, company_id)
                balance[child.parent_id.code]['value'] = balance[child.parent_id.code]['value'] + balance[child.code][
                    'value']
        else:
            codigo = value.code[val:]
            if company_id:
                data = info.filtered(lambda x: x.code == codigo and x.company_id.id == company_id)
            else:
                data = info.filtered(lambda x: x.code == codigo)
            balance_bs = 0
            balance_usd = 0
            balance_eur = 0
            for d in data:
                balance_bs = balance_bs + d.balance_bs
                balance_usd = balance_usd + d.balance_usd
                balance_eur = balance_eur + d.balance_eur
            if money == 'bs':
                balance[value.code]['value'] = balance[value.code]['value'] + round(balance_bs, 2)
            elif money == 'usd':
                balance[value.code]['value'] = balance[value.code]['value'] + round(balance_usd, 2)
            elif money == 'eur':
                balance[value.code]['value'] = balance[value.code]['value'] + round(balance_eur, 2)

    @api.multi
    def export_report(self):
        export_obj = self.env['report.export']
        context = {}
        headers = []
        context.update({
            'date_ini': self.date_ini,
            'date_end': self.date_end
        })
        if self.adjust == 'with_adjsut':
            context.update({
                'adjust': self.adjust
            })
        else:
            context.update({
                'adjust': self.adjust,
            })
        self.env['general.ledger.aleman'].with_context(context).build_view(self._cr, context)
        data_obj = self.env['general.ledger.aleman'].search([])
        bob_currency_id = self.env.ref('base.BOB')
        usd_currency_id = self.env.ref('base.USD')
        eur_currency_id = self.env.ref('base.EUR')
        report_base_cea = self.env['account.financial.html.report'].search([('id', '=', 5)])
        report_base_dsu = self.env['account.financial.html.report'].search([('id', '=', 7)])
        report_base_cea_dsu = self.env['account.financial.html.report'].search([('id', '=', 9)])
        balance = {}
        context.update({
            'tab': 'Balance General',
            'title': 'Balance General',
        })
        cells = []
        for r in self:
            if r.date_ini:
                cell = [""] * 20
                cell.insert(0, 'Fecha Inicio:')
                cell.insert(1, r.date_ini)
                cells.append(cell)
                cell = [""] * 20
                cell.insert(0, 'Fecha Fin:')
                cell.insert(1, r.date_end)
                cells.append(cell)
                cell = [""] * 20
                cells.append(cell)
            else:
                cell = [""] * 20
                cell.insert(0, 'Fecha Hasta:')
                cell.insert(1, r.date_end)
                cells.append(cell)
                cell = [""] * 20
                cells.append(cell)
            if r.currency_id:
                cell = [""] * 20
                cell.insert(0, 'Expresado en:')
                cell.insert(1, r.currency_id.symbol)
                cells.append(cell)
                cell = [""] * 20
                cells.append(cell)
            if r.company_id:
                if r.company_id.id == 1:
                    if r.currency_id.id == bob_currency_id.id:
                        if report_base_cea:
                            for line in report_base_cea.line_ids:
                                balance.update({
                                    line.code: {
                                        "value": 0,
                                        "level": line.level,
                                        'name': line.name,
                                    }
                                })
                                self.array_recursive(line, data_obj, 'bs', 1, balance, r.company_id.id)
                        else:
                            raise ValidationError(_('No se encontro una parametrizacion para generar el reporte'))
                    elif r.currency_id.id == usd_currency_id.id:
                        if report_base_cea:
                            for line in report_base_cea.line_ids:
                                balance.update({
                                    line.code: {
                                        "value": 0,
                                        "level": line.level,
                                        'name': line.name,
                                    }
                                })
                                self.array_recursive(line, data_obj, 'usd', 1, balance, r.company_id.id)
                        else:
                            raise ValidationError(_('No se encontro una parametrizacion para generar el reporte'))
                    else:
                        raise ValidationError(_('Para esta compañia el reporte solo se puede generar en Bs o $'))
                elif r.company_id.id == 3:
                    if r.currency_id.id == usd_currency_id.id:
                        if report_base_dsu:
                            for line in report_base_dsu.line_ids:
                                balance.update({
                                    line.code: {
                                        "value": 0,
                                        "level": line.level,
                                        'name': line.name,
                                    }
                                })
                                self.array_recursive(line, data_obj, 'usd', 1, balance, r.company_id.id)
                        else:
                            raise ValidationError(_('No se encontro una parametrizacion para generar el reporte'))
                    elif r.currency_id.id == eur_currency_id.id:
                        if report_base_dsu:
                            for line in report_base_dsu.line_ids:
                                balance.update({
                                    line.code: {
                                        "value": 0,
                                        "level": line.level,
                                        'name': line.name,
                                    }
                                })
                                self.array_recursive(line, data_obj, 'eur', 1, balance, r.company_id.id)
                        else:
                            raise ValidationError(_('No se encontro una parametrizacion para generar el reporte'))
                    else:
                        raise ValidationError(_('Para esta compañia el reporte solo se puede generar en en $ o €'))
            else:
                if r.currency_id.id == usd_currency_id.id:
                    if report_base_cea_dsu:
                        for line in report_base_cea_dsu.line_ids:
                            balance.update({
                                line.code: {
                                    "value": 0,
                                    "level": line.level,
                                    'name': line.name,
                                }
                            })
                            self.array_recursive(line, data_obj, 'usd', 2, balance)
                    else:
                        raise ValidationError(_('No se encontro una parametrizacion para generar el reporte'))
                elif r.currency_id.id == eur_currency_id.id:
                    if report_base_cea_dsu:
                        for line in report_base_cea_dsu.line_ids:
                            balance.update({
                                line.code: {
                                    "value": 0,
                                    "level": line.level,
                                    'name': line.name,
                                }
                            })
                            self.array_recursive(line, data_obj, 'eur', 2, balance)
                    else:
                        raise ValidationError(_('No se encontro una parametrizacion para generar el reporte'))
                else:
                    raise ValidationError(_('El reporte combinado solo se puede generar en $ o €'))
            if 'T1' in balance and 'T2' in balance:
                balance['T1']['value'] = balance['A1000']['value']
                balance['T2']['value'] = balance['A2000']['value'] + balance['A3000']['value']
                for line in report_base_cea.line_ids:
                    if balance[line.code]:
                        cell = [""] * 20
                        cell.insert(line.level, line.name)
                        if line.level >= 2:
                            cell.insert(8, balance[line.code]['value'])
                        else:
                            cell.insert(9, balance[line.code]['value'])
                        cells.append(cell)
                        self.build_excel(line, balance, cells)
            elif 'TD1' in balance and 'TD2' in balance:
                balance['TD1']['value'] = balance['D1000']['value']
                balance['TD2']['value'] = balance['D2000']['value'] + balance['D3000']['value']
                for line in report_base_dsu.line_ids:
                    if balance[line.code]:
                        cell = [""] * 20
                        cell.insert(line.level, line.name)
                        if line.level >= 2:
                            cell.insert(8, balance[line.code]['value'])
                        else:
                            cell.insert(9, balance[line.code]['value'])
                        cells.append(cell)
                        self.build_excel(line, balance, cells)
            elif 'TCD1' in balance and 'TCD2' in balance:
                balance['TCD1']['value'] = balance['AD1000']['value']
                balance['TCD2']['value'] = balance['AD2000']['value'] + balance['AD3000']['value']
                for line in report_base_cea_dsu.line_ids:
                    if balance[line.code]:
                        cell = [""] * 20
                        cell.insert(line.level, line.name)
                        if line.level >= 2:
                            cell.insert(8, balance[line.code]['value'])
                        else:
                            cell.insert(9, balance[line.code]['value'])
                        cells.append(cell)
                        self.build_excel(line, balance, cells)

            outputxls = export_obj.gen_xls(headers, cells, context)
            output64 = base64.encodestring(outputxls)
            export_id = export_obj.create({
                'name': 'BalanceGeneral.xls',
                'filename': 'BalanceGeneral.xls',
                'file': output64
            })
            if export_id:
                return {
                    'name': 'Descargar Reporte',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': False,
                    'res_model': 'report.export',
                    'domain': [],
                    'res_id': export_id.id,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }

    @api.multi
    def build_excel(self, line, balance, cells):
        if len(line.children_ids) > 0:
            for child in line.children_ids:
                cell = [""] * 20
                cell.insert(child.level, child.name)
                if line.level >= 2:
                    cell.insert(8, balance[child.code]['value'])
                else:
                    cell.insert(9, balance[child.code]['value'])
                cells.append(cell)
                self.build_excel(child, balance, cells)