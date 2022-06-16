from odoo import fields, models
#cambios para poder hacer commit


class Cajas(models.Model):
    _name = "cotizador.cajas"
    _description = "Medidas de Cajas, Peso Volumétrico, Volumen Interior en (cm3)"
    _order = "id asc"

    m_cajas = fields.Char("Medidas de Cajas")
    peso_vol = fields.Float("Peso Volumétrico")
    vol_interior = fields.Integer("Volumen interior en cmᵌ")

