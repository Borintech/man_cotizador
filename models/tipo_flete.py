# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CotizadorTipoFlete(models.Model):
    _name = 'cotizador.tipo.flete'
    _description = 'Tipo de Flete para Cotizador'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Nombre del tipo de flete'
    )
    codigo = fields.Selection(
        selection=[
            ('maritimo', 'Marítimo'),
            ('aereo', 'Aéreo'),
            ('currier', 'Currier'),
        ],
        string='Código',
        required=True,
        help='Código que se vincula con el campo medio_envio de la orden de venta'
    )
    coeficiente = fields.Float(
        string='Coeficiente',
        required=True,
        default=1.0,
        digits=(16, 4),
        help='Coeficiente a aplicar para este tipo de flete'
    )
    coef_flete = fields.Float(
        string='Coef. Flete Base',
        default=0.0,
        digits=(16, 4),
        help='Coeficiente de flete base adicional'
    )
    porcentaje_gasto_despacho = fields.Float(
        string='% Gasto Despacho',
        default=0.0,
        help='Porcentaje de gasto de despacho para este tipo de flete'
    )
    descripcion = fields.Text(
        string='Descripción',
        help='Descripción detallada del tipo de flete'
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    sequence = fields.Integer(
        string='Secuencia',
        default=10
    )

    _sql_constraints = [
        ('codigo_uniq', 'unique(codigo)', 'Solo puede existir un tipo de flete por cada código (Marítimo, Aéreo, Currier).'),
    ]

    @api.constrains('coeficiente')
    def _check_coeficiente(self):
        for record in self:
            if record.coeficiente <= 0:
                raise ValidationError(_('El coeficiente debe ser mayor a 0.'))
