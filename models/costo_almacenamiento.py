from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Transformada(models.Model):
    _name = "cotizador.costos_almacenamiento"
    _description = "Costos de almacenamiento"
    _order = "id desc"

    kg_desde = fields.Float("Kg. desde")
    kg_hasta = fields.Float("Kg. hasta")
    importe = fields.Float("Importe")
