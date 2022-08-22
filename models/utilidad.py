from odoo import fields, models
#cambios para poder hacer commit


class Utilidad(models.Model):
    _name = "cotizador.utilidad"
    _description = "Utilidad por cliente"
    _order = "id asc"

    tipo_cliente = fields.Char("Tipo de Cliente")
    porcentaje = fields.Char("Porcentaje de utilidad")


