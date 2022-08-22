# -*- coding: utf-8 -*-
#cambios para poder hacer commit

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Transformada(models.Model):
    _name = "cotizador.configuracion"
    _description = "Configuracion"
    _order = "id desc"

    precio_dolar = fields.Float("P.Dolar")
    precio_euro = fields.Float("P.Euro")
    precio_dolar_blue = fields.Float("P.Dolar Blue")
    coef_peso_adicional = fields.Float("Peso adicional (bobina/palet)")
    # coef_peso_ajuste = 1.20
    coef_peso_ajuste = fields.Float("Variación Peso")

    #coef_flete = fields.Float("Coef Flete")

    #coef_dexport = 25
    coef_dexport =  fields.Float("D. Importación %")


    #coef_utilidad = 1.60
    coef_utilidad = fields.Float("Utilidad %")

    # coeficientes para el flete

    coef_flete_maritimo = fields.Float("Coef T. Marítimo", default=5)
    coef_flete_aereo = fields.Float("Coef T. Aéreo", default=15)
    coef_flete_currier = fields.Float("Coef T. Currier", default=25)

    # porcentaje para el gasto de despacho cuando es marítimo
    porcentaje_gasto_maritimo = fields.Float("Gasto Despacho Marítimo %")

    # porcentaje para el gasto de despacho cuando es aéreo
    porcentaje_gasto_aereo = fields.Float("Gasto Despacho Aéreo %")
