# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Transformada(models.Model):
    _name = "cotizador.analitico"
    _description = "Analítico Cotizador"
    _order = "id desc"

    nro_orden = fields.Char("Nro Orden")
    #sale_order = fields.Many2one("sale.order")

    precio_dolar = fields.Float("P.Dolar")
    precio_euro = fields.Float("P.Euro")

    subtotal1 = fields.Float("Subtotal 1")
    total_peso =  fields.Float("Peso total")
    coef_peso_ajuste  =  fields.Float("Coef Peso")

    #total_peso_ajustado = (total_peso * coef_peso_ajsute)
    total_peso_ajustado =  fields.Float("Peso Total Ajustado ")

    # coef_subtotal2 = 1.20
    coef_flete = fields.Float("Coef Flete")

    subtotal2_flete =  fields.Float("Subtotal2 Felte")

    #coef_dexport = 25
    coef_dexport =  fields.Float("Coef Exp")

    #subtotal3_dexport =  (coef_dexport * subtotal2_flete)
    subtotal3_dexport =  fields.Float("Subtotal3 Exp")

    #coef_utilidad = 1.60
    coef_utilidad = fields.Float("Coef Utilidad ")

    #subtotal4_utilidad = (subtotal3_dexport * coef_utilidad)
    subtotal4_utilidad = fields.Float("Subtotal3 Utilidad")

    #total_almacenaje_dolares =  ver tabla de peso y dias
    gastos_envio_local = fields.Float("Gastos Env Local")

    gastos_envios_despacho = fields.Float("Gastos Env Despacho")

    #subtotal5 = gastos_envio_local + gastos_envios_despacho + total_almacenaje_dolares + subtotal4_utilidad
    subtotal5_gastos = fields.Float("Subtotal5 Gastos")

    #coef_cotizador = subtotal5 / subtotal1
    coef_cotizador = fields.Float("Coef Cotizacion")
