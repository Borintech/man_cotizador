from odoo import fields, models


class Bobinas(models.Model):
    _name = "cotizador.bobinas"
    _description = "Medidas de Bobinas, peso bruto y peso volumétrico"
    _order = "id asc"

    m_bobinas = fields.Char("Medidas de Bobinas")
    peso_bruto = fields.Float("Peso Bruto")
    peso_vol = fields.Float("Peso Volumétrico")

