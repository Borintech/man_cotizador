# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Transformada(models.Model):
    _name = "cotizador.configuracion"
    _description = "Configuracion"
    _order = "id desc"

    precio_dolar = fields.Float("P.Dolar")
    precio_euro = fields.Float("P.Euro")

    # coef_peso_ajuste = 1.20
    coef_peso_ajuste  =  fields.Float("Coef Peso")

    coef_flete = fields.Float("Coef Flete")

    #coef_dexport = 25
    coef_dexport =  fields.Float("Coef Exp")


    #coef_utilidad = 1.60
    coef_utilidad = fields.Float("Coef Utilidad ")

    # coeficientes para el flete

    coef_flete_maritimo = fields.Float("Coef T. Marítimo", default=5)
    coef_flete_aereo = fields.Float("Coef T. Aéreo", default=15)
    coef_flete_currier = fields.Float("Coef T. Currier", default=25)